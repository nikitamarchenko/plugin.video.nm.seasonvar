import os
import os.path


PLUGIN_NAME = 'plugin.video.nm.seasonvar'
PLUGIN_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          PLUGIN_NAME)
ADDON_METADATA = os.path.join(PLUGIN_DIR, 'addon.xml')


if __name__ == '__main__':
    import xml.etree.ElementTree
    e = xml.etree.ElementTree.parse(ADDON_METADATA).getroot()
    print e.attrib['version']
