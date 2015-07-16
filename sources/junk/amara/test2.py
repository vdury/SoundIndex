from amara.writers import lookup
import amara
from amara import tree
HTML_W = lookup("html")
xml_write(writer=HTML_W, stream=my_file, encoding='iso-8859-1')
