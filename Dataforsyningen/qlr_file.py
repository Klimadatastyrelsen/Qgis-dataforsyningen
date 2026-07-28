import urllib.parse
from qgis.PyQt import QtXml
from qgis.core import QgsMessageLog


def log_message(message):
    QgsMessageLog.logMessage(message, "Dataforsyningen plugin")


class QlrFile(object):
    def __init__(self, xml):
        self.doc = QtXml.QDomDocument()
        contentSet = self.doc.setContent(xml)

        if not contentSet:
            log_message("Failed to parse XML content")

    def get_groups_with_layers(self):
        # result: [{'name': groupName, 'layers': [{'name': layerName, 'id': layerId}]}]
        result = []
        groups = self.doc.elementsByTagName("layer-tree-group")
        i = 0
        while i < groups.count():
            group = groups.at(i)
            group_name = None
            if (
                group.toElement().hasAttribute("name")
                and group.toElement().attribute("name") != ""
            ):
                group_name = group.toElement().attribute("name")
                layers = self.get_group_layers(group)
                if layers and group_name:
                    result.append({"name": group_name, "layers": layers})
            i += 1
        return result

    def get_group_layers(self, group_node):
        # result:[{'name': layerName, 'id': layerId}]
        result = []
        child_nodes = group_node.childNodes()
        i = 0
        while i < child_nodes.count():
            node = child_nodes.at(i)
            if node.nodeName() == "layer-tree-layer":
                layer_name = node.toElement().attribute("name")
                layer_id = node.toElement().attribute("id")
                layer_source = node.toElement().attribute("source")
                params = urllib.parse.parse_qs(layer_source)

                if "url" in params:
                    wms_url = params["url"][0]
                    layer_provider = urllib.parse.urlparse(wms_url).netloc
                else:
                    # Handle case where 'url' parameter is missing from source
                    layer_provider = urllib.parse.urlparse(layer_source)
                    layer_provider = urllib.parse.urlparse(
                        layer_provider.path.split("url='")[1].split("'")[0]
                    ).netloc

                maplayer_node = self.get_maplayer_node(layer_id)
                if maplayer_node:
                    service = self.get_maplayer_service(maplayer_node)
                    if service:
                        result.append(
                            {
                                "name": layer_name,
                                "id": layer_id,
                                "service": service,
                                "provider": layer_provider,
                            }
                        )
            i += 1
        return result

    def get_maplayer_service(self, maplayer_node):
        datasource_node = None
        service = None
        datasource_nodes = maplayer_node.toElement().elementsByTagName("datasource")
        if datasource_nodes.count() == 1:
            datasource_node = datasource_nodes.at(0)
            datasource = datasource_node.toElement().text()
            url_part = None
            datasource_parts = datasource.split("&") + datasource.split(" ")
            for part in datasource_parts:
                if part.startswith("url"):
                    url_part = part

            if url_part:
                from_ix = url_part.index("=") + 1
                url_only = url_part[from_ix:]
                url_path = urllib.parse.urlparse(url_only).path
                url_path = url_path[1:]
                url_split = url_path.lstrip("https://").split("/")
                # i.e. base_url/service/
                if len(url_split) < 2:
                    service = url_path
                # standard url split
                # i.e. base_url/type/service/
                else:
                    service = url_split[1]
        return service

    def get_maplayer_node(self, id):
        node = self.getFirstChildByTagNameValue(
            self.doc.documentElement(), "maplayer", "id", id
        )
        return node

    def getFirstChildByTagNameValue(self, elt, tagName, key, value):
        nodes = elt.elementsByTagName(tagName)
        i = 0
        while i < nodes.count():
            node = nodes.at(i)
            idNode = node.namedItem(key)
            if idNode is not None:
                child = idNode.firstChild().toText().data()
                # layer found
                if child == value:
                    return node
            i += 1
        return None
