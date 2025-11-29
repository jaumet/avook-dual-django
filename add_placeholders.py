import os
import polib

def add_placeholder_translations(locale_dir):
    for lang_code in os.listdir(locale_dir):
        po_file_path = os.path.join(locale_dir, lang_code, 'LC_MESSAGES', 'django.po')
        if os.path.exists(po_file_path):
            print(f"Processing {po_file_path}...")
            po = polib.pofile(po_file_path)
            for entry in po:
                if not entry.msgstr:
                    entry.msgstr = f'[{lang_code}] {entry.msgid}'
            po.save()
            print(f"Finished processing {po_file_path}.")

if __name__ == "__main__":
    add_placeholder_translations('locale')
