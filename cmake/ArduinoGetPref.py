import os
import os.path
import subprocess
import argparse
import re

def check_output(args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = process.communicate()
    return out

class PreferenceCenter(dict):
    def load_from_content(self, content):
        for aline in content.splitlines():
            if "=" not in aline:
                continue

            index = aline.find("=")
            if index < 0:
                continue

            self[aline[:index].strip()] = aline[index + 1:]

    def _generate_prefix_key(self, parent_key, suffix_key):
        parent_key_parties = parent_key.split(".")
        suffix_key_parties = suffix_key.split(".")

        if len(parent_key_parties) > len(suffix_key_parties):
            prefix_length = len(parent_key_parties) - len(suffix_key_parties)
            generated_key_parties = (parent_key_parties[:prefix_length] +
                suffix_key_parties)
            generated_key = ".".join(generated_key_parties)
            if parent_key == generated_key:
                del parent_key_parties[len(parent_key_parties) - 1]
                generated_key = self._generate_prefix_key(".".join(parent_key_parties), suffix_key)
        else:
            generated_key = suffix_key

        return generated_key

    def get_expanded(self, key):
        key = key.strip()
        raw_preference = self.get(key)

        expanded = raw_preference
        if raw_preference is not None:
            replace_marks = re.findall(r"\{([^\}]+)\}", raw_preference)
            for amark in replace_marks:
                replacement = self.get_expanded(amark)
                if replacement is None:
                    prefixed_key = self._generate_prefix_key(key, amark)
                    if prefixed_key != key:
                        replacement = self.get_expanded(prefixed_key)

                if replacement is None:
                    raise Exception(
                        "Failed to expand arduino environment variant \"%s\" for \"%s=%s\"" %
                        (amark, key, raw_preference))

                expanded = expanded.replace("{%s}" % amark, replacement)

        return expanded


class Application(object):
    def __init__(self):
        parser = argparse.ArgumentParser(description='Get preference from Arduino IDE.')
        parser.add_argument('key', help='Preference Key')
        parser.add_argument(
            "--predefined", "-p",
            default="",
            help='Predefined preferences, for ex: "abc=1; kknd=2" .')

        self._args = parser.parse_args()
        self._preferences = PreferenceCenter()

    def exec_(self):

        self._preferences.load_from_content(self._args.predefined.replace(";", "\n"))

        # Load preferences from Arduino IDE
        preference_file_path = "./ArduinoPrefs"
        preference_content = ""
        if os.path.exists(preference_file_path):
            with open(preference_file_path, "rb") as afile:
                preference_content = afile.read()
        else:
            preference_content = check_output(["arduino", "--get-pref"])
            with open(preference_file_path, "wb") as afile:
                afile.write(preference_content)

        self._preferences.load_from_content(preference_content)

        arduino_ide_path = self._preferences.get_expanded("runtime.ide.path")
        arduino_platform_path = self._preferences.get_expanded("runtime.platform.path")

        # Parse boards.txt, platform.txt, programmers.txt
        with open("%s/boards.txt" % arduino_platform_path) as afile:
            self._preferences.load_from_content(afile.read())

        with open("%s/platform.txt" % arduino_platform_path) as afile:
            self._preferences.load_from_content(afile.read())

        with open("%s/programmers.txt" % arduino_platform_path) as afile:
            self._preferences.load_from_content(afile.read())

        preference = self._preferences.get_expanded(self._args.key)
        if preference is not None:
            print(preference)

def main():
    a = Application()
    return a.exec_()

if __name__ == "__main__":
    # execute only if run as a script
    main()
