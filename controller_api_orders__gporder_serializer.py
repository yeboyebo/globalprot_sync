from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.api.sync.base.serializers.aqserializer import AQSerializer

from controllers.api.sync.orders.serializers.gporder_line_serializer import GpOrderLineSerializer


class GpOrderSerializer(AQSerializer):

    def get_data(self):

        codserie = ""
        coddivisa = ""
        datoscliente = self.get_datoscliente()
        # if "codserie" not in datoscliente or codserie is None or codserie == "":
        #     codserie = self.get_codserie()
        # else:
        #     codserie = datoscliente["codserie"]
        codejercicio = self.get_codejercicio()
        if codejercicio is None or codejercicio == "":
            codejercicio = "2019"
        if "coddivisa" not in datoscliente or coddivisa is None or coddivisa == "":
            coddivisa = "EUR"
        else:
            coddivisa = datoscliente["coddivisa"]

        codserie = self.get_codserie()
        codalmacen = "GEN"
        self.set_string_value("codserie", codserie)
        self.set_string_value("codejercicio", codejercicio)

        numero = qsatype.FactoriaModulos.get("flfacturac").iface.siguienteNumero(codserie, codejercicio, u"npedidoscli")
        codigo = qsatype.FactoriaModulos.get('flfacturac').iface.pub_construirCodigo(codserie, codejercicio, numero)
        self.set_string_value("codigo", codigo, max_characters=15)
        self.set_string_value("coddivisa", coddivisa)
        self.set_string_value("codalmacen", codalmacen)
        self.set_string_relation("fecha", "fecha", max_characters=10)
        self.set_string_relation("fechasalida", "fecha", max_characters=10)

        self.set_data_value("editable", True)
        self.set_data_value("tasaconv", 1)
        self.set_data_relation("total", "total")
        self.set_data_relation("neto", "neto")
        self.set_data_relation("totaliva", "totaliva")
        self.set_data_value("totaleuros", self.init_data["total"])
        self.set_string_value("idpedidoweb", self.init_data["idpedidoweb"], max_characters=10)

        if datoscliente:
            self.set_string_value("codcliente", datoscliente["codcliente"], max_characters=10)
            self.set_string_value("cifnif", datoscliente["cifnif"], max_characters=20)
            self.set_string_relation("coddir", "coddir", max_characters=10)
            # self.set_string_value("coddir", datoscliente["coddir"], max_characters=10)
            idceco = qsatype.FLUtil.quickSqlSelect("gp_cecoscliente", "idceco", "codcliente = '{}' AND codcentro = '{}'".format(datoscliente["codcliente"], self.init_data["codcentro"]))
            if idceco:
                self.set_string_value("idceco", idceco, max_characters=10)

        #     self.set_string_value("email", datoscliente["email"], max_characters=100)
        #     self.set_string_value("nombrecliente", datoscliente["nombre"], max_characters=100)

        #     self.set_string_value("codpostal", datoscliente["codpostal"], max_characters=10)
        #     self.set_string_value("ciudad", datoscliente["ciudad"], max_characters=100)
        #     self.set_string_value("provincia", datoscliente["provincia"], max_characters=100)
        #     self.set_string_value("codpais", datoscliente["codpais"], max_characters=20)
        #     self.set_string_value("telefono1", datoscliente["telefono1"], max_characters=30)

        #     self.set_string_value("dirtipovia", datoscliente["dirtipovia"], max_characters=100)
        #     self.set_string_value("direccion", datoscliente["direccion"], max_characters=100)
        #     self.set_string_value("dirnum", datoscliente["dirnum"], max_characters=100)
        #     self.set_string_value("dirotros", datoscliente["dirotros"], max_characters=100)
        # else:
        self.set_string_relation("email", "email", max_characters=100)
        self.set_string_relation("cifnif", "cif", max_characters=20, default="-")

        self.set_string_relation("codpostal", "direccion_cliente//codpostal", max_characters=10)
        self.set_string_relation("ciudad", "direccion_cliente//ciudad", max_characters=100)
        self.set_string_relation("provincia", "direccion_cliente//provincia", max_characters=100)
        self.set_string_relation("codpais", "direccion_cliente//codpais", max_characters=20)
        self.set_string_relation("telefono1", "direccion_cliente//telefono", max_characters=30)

        nombrecliente = "{} {}".format(self.init_data["direccion_cliente"]["nombre"], self.init_data["direccion_cliente"]["apellidos"])
        self.set_string_value("nombrecliente", nombrecliente, max_characters=100)

        self.set_string_relation("dirtipovia", "direccion_cliente//tipovia", max_characters=100)
        self.set_string_relation("direccion", "direccion_cliente//direccion", max_characters=100)
        self.set_string_relation("dirnum", "direccion_cliente//dirnum", max_characters=100)
        self.set_string_relation("dirotros", "direccion_cliente//dirotros", max_characters=100)

        # self.set_string_value("hora", self.get_hora())
        # self.set_string_value("codpago", self.get_codpago(), max_characters=10)
        self.set_string_relation("codpago", "codpago", max_characters=10)

        if "lines" not in self.data["children"]:
            self.data["children"]["lines"] = []

        for item in self.init_data["items"]:
            line_data = GpOrderLineSerializer().serialize(item)
            if "referencia" in line_data and line_data["referencia"] == "ERRORNOREFERENCIA":
                return False
            self.data["children"]["lines"].append(line_data)
        return True

    def get_codserie(self):
        codserie = "TW"

        return codserie

    def get_codejercicio(self):
        date = self.init_data["fecha"][:10]
        splitted_date = date.split("-")

        return splitted_date[0]

    def get_hora(self):
        hour = self.init_data["fecha"][-(8):]
        hour = "23:59:59" if hour == "00:00:00" else hour

        return hour

    def get_codpago(self):
        codpago = qsatype.FLUtil.quickSqlSelect("formaspago", "codpago", "descripcion = '{}'".format(self.init_data["codpago"]))

        if not codpago:
            codpago = qsatype.FactoriaModulos.get('flfactppal').iface.pub_valorDefectoEmpresa("codpago")

        return codpago

    def get_datoscliente(self):
        usuario = self.init_data["uid"]
        datos_cliente = {}
        q = qsatype.FLSqlQuery()
        # q.setSelect("c.codcliente, c.cifnif, c.codserie,c.coddivisa, c.nombre, c.telefono1, c.email, dc.id, dc.dirtipovia, dc.dirnum, dc.direccion, dc.codpostal, dc.ciudad, dc.provincia, dc.codpais, dc.dirotros")
        q.setSelect("c.codcliente, c.cifnif, dc.id")
        q.setFrom("clientes c INNER JOIN gp_usutiendaonline us ON c.codcliente = us.codcliente LEFT OUTER JOIN dirclientes dc ON c.codcliente = dc.codcliente")
        # q.setWhere("us.uid = '{}' AND dc.domenvio".format(usuario))
        q.setWhere("us.uid = '{}'".format(usuario))
        if not q.exec_():
            return False
        if q.first():
            datos_cliente["codcliente"] = q.value("c.codcliente")
            datos_cliente["cifnif"] = q.value("c.cifnif")
            # datos_cliente["nombre"] = q.value("c.nombre")
            # datos_cliente["codserie"] = q.value("c.codserie")
            # datos_cliente["coddivisa"] = q.value("c.coddivisa")
            # datos_cliente["telefono1"] = q.value("c.telefono1")
            # datos_cliente["email"] = q.value("c.email")

            datos_cliente["coddir"] = q.value("dc.id")
            # datos_cliente["dirnum"] = q.value("dc.dirnum")
            # datos_cliente["dirtipovia"] = q.value("dc.dirtipovia")
            # datos_cliente["direccion"] = q.value("dc.direccion")
            # datos_cliente["codpostal"] = q.value("dc.codpostal")
            # datos_cliente["ciudad"] = q.value("dc.ciudad")
            # datos_cliente["provincia"] = q.value("dc.provincia")
            # datos_cliente["codpais"] = q.value("dc.codpais")
            # datos_cliente["dirotros"] = q.value("dc.dirotros")

        return datos_cliente
