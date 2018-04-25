#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os.path
import os
from xml.dom import minidom


class XmlCFD(object):
    """
       Esta clase se encarga de realizar todas las operaciones relacionadas
       con la manipulación del archivo xml de facturación electrónica
    """
    nomFileXml = ''

    def __init__(self, nomFileXml):
        """ Initialize instance. """
        self.nomFileXml = nomFileXml
        self.atributos = dict()
        self.articulos = dict()

    @property
    def getAtributos(self):
        """ Regresa los atributos necesario para formar el nombre del archivo. """
        reload(sys)
        sys.setdefaultencoding("utf-8")
        if os.path.isfile(self.nomFileXml.decode('latin-1').encode("utf-8")):
            try:
                xmlDoc = minidom.parse(self.nomFileXml.decode('latin-1').encode("utf-8"))
                nodes = xmlDoc.childNodes
                comprobante = nodes[0]
                compAtrib = dict(comprobante.attributes.items())
            except Exception:
                pass
            # Se trunca la parte de la hora de emisión
            self.atributos['fecha'] = compAtrib['Fecha'][0:10]
            self.atributos['total'] = compAtrib['Total']#.rjust(10, '0')
            self.atributos['subTotal'] = compAtrib['SubTotal']

            for nodo in comprobante.getElementsByTagName("cfdi:Impuestos"):
                self.atributos['IVA'] = nodo.getAttribute('TotalImpuestosTrasladados')

            emisor = comprobante.getElementsByTagName('cfdi:Emisor')
            self.atributos['rfc'] = emisor[0].getAttribute('Rfc')
            self.atributos['nombre'] = emisor[0].getAttribute('Nombre')
            timbre = comprobante.getElementsByTagName('tfd:TimbreFiscalDigital')
            try:
                self.atributos['UUiD'] = timbre[0].getAttribute('UUID')
            except KeyError:
                self.atributos['UUiD'] = ' '
            conceptos = comprobante.getElementsByTagName('cfdi:Conceptos')
            concept = conceptos[0].getElementsByTagName('cfdi:Concepto')
            x = 0
            for nodo in concept:
                x += 1
                if nodo.hasAttribute("descripcion"):
                    self.articulos['importe' + str(x)] = nodo.getAttribute('importe')
                    self.articulos['valorUnitario' + str(x)] = nodo.getAttribute('valorUnitario')
                    self.articulos['descripcion' + str(x)] = nodo.getAttribute('descripcion')
                    self.articulos['cantidad' + str(x)] = nodo.getAttribute('cantidad')
        return self.atributos

    @property
    def getArticulos(self):
        """ Regresa los atributos necesario para formar el nombre del archivo. """
        reload(sys)
        sys.setdefaultencoding("utf-8")
        if os.path.isfile(self.nomFileXml.decode('latin-1').encode("utf-8")):
            try:
                xmlDoc = minidom.parse(self.nomFileXml.decode('latin-1').encode("utf-8"))
                nodes = xmlDoc.childNodes
                comprobante = nodes[0]
            except Exception:
                pass
            for nodo in comprobante.getElementsByTagName("cfdi:Conceptos"):
                x=0
                for nodo2 in nodo.getElementsByTagName("cfdi:Concepto"):
                    x += 1
                    self.articulos['importe'+str(x)] = nodo2.getAttribute('Importe')
                    self.articulos['valorUnitario'+str(x)] = nodo2.getAttribute('ValorUnitario')
                    self.articulos['descripcion'+str(x)] = nodo2.getAttribute('Descripcion')
                    self.articulos['cantidad'+str(x)] = nodo2.getAttribute('Cantidad')
        return self.articulos