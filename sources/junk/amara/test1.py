import amara
from amara import tree
from amara.writers import lookup

MONTY_XML = """<monty>
<python span = "eggs">What do you mean jqsdlmk</python>
<python ministry="abuse"> But I was looking for argument</python>
</monty>"""

doc = amara.parse(MONTY_XML)
assert doc.xml_type == tree.entity.xml_type
m = doc.xml_children[0]

assert m.xml_parent == doc

#print m.xml_local
#print m.xml_qname

assert m.xml_prefix == None
assert m.xml_qname == m.xml_local

assert m.xml_namespace == None
assert m.xml_name == (None, u'monty')

p1 = m.xml_children[1]
p1.xml_attributes[(None, u'span')] = u"greeneggs"
p1.xml_children[0].xml_value = u"Close to the edit"
HTML_W = lookup("html")
p1.xml_write(writer=HTML_W, stream="bla.html", encoding='iso-8859-1')

