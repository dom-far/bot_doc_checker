import os
import zipfile
import tempfile
from lxml import etree

def remove_NULL_from_rels(data):
    ET = etree.fromstring(data)
    rels_to_remove = []
    for node in ET.iter():
        if node.attrib.get('Target') == 'NULL':
            rels_to_remove.append(node.attrib['Id'])
            node.getparent().remove(node)
    return etree.tostring(ET, xml_declaration=True), rels_to_remove

def remove_rels_from_slide(data, rels):
    ET = etree.fromstring(data)
    for node in ET.iter():
        for rId in rels:
            if rId in node.attrib.values():
                node.getparent().remove(node)
    return etree.tostring(ET, xml_declaration=True)

def fixCorruptedPPTX(zipname):
    # generate a temp file
    tmpfd, tmpname = tempfile.mkstemp(dir=os.path.dirname(zipname))
    os.close(tmpfd)

    # create a temp copy of the archive without filename            
    with zipfile.ZipFile(zipname, 'r') as zin:
        with zipfile.ZipFile(tmpname, 'w') as zout:
            zout.comment = zin.comment # preserve the comment
            rels_xml_mapping = {}
            modified_xml = {}
            modified_rels = {}
            for item in zin.infolist():
                if item.filename.endswith('.rels'):
                    rels_file = item.filename
                    rels_dir, rels_name = os.path.split(rels_file)
                    rels_data = zin.read(rels_file)
                    rels_data, rels_to_remove = remove_NULL_from_rels(rels_data)
                    xml_file = os.path.join(os.path.split(rels_dir)[0], rels_name.rsplit('.', 1)[0])
                    if len(rels_to_remove) > 0 and xml_file in zin.namelist():
                        xml_data = zin.read(xml_file)
                        xml_data = remove_rels_from_slide(xml_data, rels_to_remove)
                        modified_xml[xml_file] = xml_data
                        modified_rels[rels_file] = rels_data
                
            for item in zin.infolist():
                if item.filename not in modified_xml and item.filename not in modified_rels:
                    zout.writestr(item, zin.read(item.filename))
                    
    # replace with the temp archive
    os.remove(zipname)
    os.rename(tmpname, zipname)

    # now add filename with its new data
    with zipfile.ZipFile(zipname, mode='a', compression=zipfile.ZIP_DEFLATED) as zf:
        for rels_file, rels_data in modified_rels.items():
            zf.writestr(rels_file, rels_data)
        for xml_file, xml_data in modified_xml.items():
            zf.writestr(xml_file, xml_data)

def fix(path_file: str) -> None:
    fixCorruptedPPTX(path_file)