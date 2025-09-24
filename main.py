import xml.etree.ElementTree as ET
import os

class RobloxXMLExtractor:
    def __init__(self, xml_path, output_dir):
        self.xml_path = xml_path
        self.output_dir = output_dir
        self.src_dir = os.path.join(output_dir, "src")
        self.script_classes = {"Script", "LocalScript", "ModuleScript"}
        os.makedirs(self.src_dir, exist_ok=True)

    def sanitize(self, name):
        return "".join(c if c.isalnum() or c in "._- " else "_" for c in (name or ""))

    def get_name(self, instance):
        for prop in instance.findall('Properties/*'):
            if prop.attrib.get("name") == "Name":
                return prop.text or "Unnamed"
        return "Unnamed"

    def ensure_dir(self, path):
        os.makedirs(path, exist_ok=True)

    def unique_path(self, path):
        base_path = path
        i = 1
        while os.path.exists(path):
            path = f"{base_path}_{i}"
            i += 1
        return path

    def extract_instance(self, instance, path):
        name = self.sanitize(self.get_name(instance)) or "Unnamed"
        instance_path = self.unique_path(os.path.join(path, name))
        self.ensure_dir(instance_path)

        class_name = instance.attrib.get('class', 'Unknown')
        if class_name in self.script_classes:
            script_file = os.path.join(instance_path, f"{name}.luau")
            self.ensure_dir(os.path.dirname(script_file))
            for prop in instance.findall('Properties/*'):
                if prop.tag == "ProtectedString" and prop.attrib.get("name") == "Source":
                    with open(script_file, "w", encoding="utf-8") as f:
                        f.write(prop.text or "")
                    break
            else:
                with open(script_file, "w", encoding="utf-8") as f:
                    f.write("-- No source found\n")

        props = {prop.attrib.get("name"): prop.text for prop in instance.findall('Properties/*')}
        if props:
            props_file = os.path.join(instance_path, f"{name}_properties.txt")
            self.ensure_dir(os.path.dirname(props_file))
            try:
                with open(props_file, "w", encoding="utf-8") as f:
                    for k, v in props.items():
                        f.write(f"{k}: {v}\n")
            except Exception as e:
                print(f"Failed to write properties for {instance_path}: {e}")

        for child in instance.findall('Item'):
            try:
                self.extract_instance(child, instance_path)
            except Exception as e:
                print(f"Failed to extract child {self.get_name(child)} ({child.attrib.get('class')}) in {instance_path}: {e}")

    def run(self):
        tree = ET.parse(self.xml_path)
        root = tree.getroot()
        print("Top-level Items found:")
        for item in root.findall("Item"):
            print(f"- {item.attrib.get('class')} ({self.get_name(item)})")
            try:
                self.extract_instance(item, self.src_dir)
            except Exception as e:
                print(f"Failed to extract {self.get_name(item)} ({item.attrib.get('class')}): {e}")
        print("[*DUMP COMPLETE*]")

print("[*] Made by Ayham")
xml_file = input("Enter XML File[>]  ").strip()
out_dir = "."
RobloxXMLExtractor(xml_file, out_dir).run()
input("\nPress Enter to exit...")
