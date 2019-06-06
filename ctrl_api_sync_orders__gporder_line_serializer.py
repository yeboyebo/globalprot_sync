from YBLEGACY import qsatype
from YBLEGACY.constantes import *

from controllers.base.default.serializers.default_serializer import DefaultSerializer


class GpOrderLineSerializer(DefaultSerializer):

    def get_data(self):
        iva = self.init_data["iva"]
        if not iva or iva == "":
            iva = 0

        datostalla = self.get_datostalla()
        if datostalla:
            self.set_string_value("referencia", datostalla["referencia"], max_characters=18)
            self.set_string_value("barcode", datostalla["barcode"], max_characters=20)
            self.set_string_value("talla", datostalla["talla"], max_characters=5)
            self.set_string_value("color", datostalla["color"], max_characters=15)
            descripcion = self.get_descripcion(datostalla["referencia"])
        else:
            referencia = self.get_referencia()
            self.set_string_value("referencia", self.get_referencia(), max_characters=18)
            descripcion = self.get_descripcion(referencia)

        if descripcion == "" or descripcion is None:
            descripcion = self.init_data["descripcion"]

        self.set_string_value("descripcion", descripcion, max_characters=100)
        self.set_string_value("codimpuesto", self.get_codimpuesto(iva), max_characters=10)

        self.set_data_value("cantidad", self.get_cantidad())

        self.set_data_value("pvpunitario", self.init_data["pvpunitario"])
        self.set_data_value("pvpsindto", self.init_data["pvpsindto"])
        self.set_data_value("pvptotal", self.init_data["pvptotal"])
        self.set_data_value("dtopor", self.init_data["dtopor"])
        self.set_data_value("dtolineal", self.init_data["dtolineal"])
        self.set_data_value("iva", iva)
        # self.set_data_relation("iva", iva)
        return True

    def get_referencia(self):
        product_id = self.init_data["product_id"]
        referencia = qsatype.FLUtil.quickSqlSelect("articulos", "referencia", "product_id = '{}'".format(product_id))
        if not referencia:
            return "ERRORNOREFERENCIA"
        return referencia

    def get_descripcion(self, referencia):
        return qsatype.FLUtil.quickSqlSelect("articulos", "descripcion", "referencia = '{}'".format(referencia))

    def get_codimpuesto(self, iva):
        if parseFloat(iva) > 0:
            return "GEN"
        else:
            return "EXT"

    def get_cantidad(self):
        return self.init_data["cantidad"]

    def get_datostalla(self):
        product_id = self.init_data["product_id"]
        datos_talla = {}
        q = qsatype.FLSqlQuery()
        q.setSelect("referencia, barcode, talla, color")
        q.setFrom("atributosarticulos")
        q.setWhere("product_id = '{}'".format(product_id))
        if not q.exec_():
            return False
        if q.first():
            datos_talla["referencia"] = q.value("referencia")
            datos_talla["barcode"] = q.value("barcode")
            datos_talla["talla"] = q.value("talla")
            datos_talla["color"] = q.value("color")

        return datos_talla
