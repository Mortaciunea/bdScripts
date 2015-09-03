import xml.sax

from xml.sax import ContentHandler, SAXParseException
from xml.sax import make_parser

class bdXMLHandler(ContentHandler):
    def __init__(self):
        self.productName = []
        self.module = []
        self.address = []
        self.weaponList = {}
        
        self.desc = False
    
    def startElement(self,name,attrs):
        if name == 'weapon':
            #self.productName.append(attrs.get('name',"N/A"))
            print attrs.get('name',"N/A")
            #self.module.append(attrs.get('module',"N/A"))
            print attrs.get('category',"N/A")
            self.weaponList[attrs.get('name',"N/A")] = attrs.get('category',"N/A") 
        '''
        elif name == 'address':
            self.address.append(attrs.get('org',"N/A"))
            print attrs.get('org',"N/A")
            self.address.append(attrs.get('street',"N/A"))
            print attrs.get('street',"N/A")
        elif name == 'description':
            self.desc = True
        return
    	'''
    	
    def characters(self,ch):
        if self.desc:
            print ch
            
    def endElement(self,name):
        if name == 'description':
            self.desc = False
            print '\n'

parser = make_parser()
parser.setContentHandler(bdXMLHandler())

parser.parse('h:\\weaponList.xml')

            