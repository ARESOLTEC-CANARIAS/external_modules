from odoo import models, fields


class SaleOrder(models.Model):
    _inherit = "sale.order"
    show_logo = fields.Boolean("Show logo")
    hide_total = fields.Boolean("Hide total")
    contract = fields.Boolean("Annex conditions(contracts)")
    ot_andamio = fields.Char(string="O.T")
    po_andamio = fields.Char(string="P.O")
    valorado = fields.Boolean(string="Non valued Single Report")
    introduccion = fields.Html(
        string="Introduction",
        translate=True,
        default="Estimados señores:<br> <br>Conforme a sus deseos nos es grato someter a estudio y aprobación la siguiente oferta de suministro e instalación de andamios para sus trabajos en:",
    )
    alcance_contenido = fields.Html(
        string="Scope and economic content of the offer",
        translate=True,
        default="Sistema de Andamios Multidireccionales, fabricados de acero AE 275B, siendo los tubos que forman la estructura portante de 48,3mm y espesor 3,1mm, con un límite elástico minimo garantizado de 360 N/nm2. La protección superfial del material se consigue a base de cinc en un proceso de galvanizado que asegura, por norma, un recubrimiento mínimo de 56µ. Certificados por la entidad AENOR (certificado nºA34/000007) conforme con las normas UNE -EN12810- 1:2005 <br/> Los andamios siempre se instalarán con doble barandilla de seguridad, rodapié exterior, escala de acceso, con los arriostres necesarios y niveles de plataformas metálicos "
    )
    servicio_minimo = fields.Html(
        string="Minimum service",
        translate=True,
        default="<b>Servicio mínimo:</b> <br/><br/>  El mínimo de m<sup>3</sup> a facturar por andamios será de 13m<sup>3</sup> <br/><br/>  En el caso que se deban realizar trabajos nocturnos de duración a inferior a una semana, el cliente deberá asumir las 8 horas laborables del dia siguiente al trabajo nocturno por trabajador, puesto que estos deberán descansar la jornada entera del dia siguiente al trabajo nocturno. Se nos deberá comunicarse con una antelación de 24h la necesidad de trabajos nocturnos. <br/><br/>  Siempre que no se requiera presencia permanente de personal en obra y los servicios de instalación sean esporádicos: maniobras, modificaciones etc. se cobrarán además de los metros cúbicos que se pudieran generar, los siguientes conceptos:<br/> <i>Por llamada o servicio: 4 horas de servicio + horas de montaje(administración*)+m<sup>3</sup> montados <br/><br/> </i> <b>Nota:</b> Se considerará esporádico todo aquel trabajo no comunicado a los mandos de Ateca con una antelación a 12 Horas.",
    )
    forma_condiciones_pago = fields.Html(
        string="Payment terms and conditions",
        translate=True,
        default="30 días finalización de trabajo",
    )
    condiciones_generales = fields.Html(
        string="General terms and conditions",
        translate=True,
        default="Las condiciones generales de la empresa ATECA que se adjuntancomo anexo a la oferta y que las partes declaran a conocer y aceptar forman parte integrante e inseparable de la oferta y su aceptación ",
    )
    conforme_aceptacion_partes = fields.Html(
        string="Conformity and acceptance by the parties",
        translate=True,
        default="En caso de aceptar el contenido íntegro de este contrato, incluyendo las Condiciones Generales, les rogamos lo remitan copia debidamente firmada y sellada en todas sus hojas, y en ellos prueba de conformidad. <br/><br/>  Sin otro particular y la espera de sus noticias, reciban un cordial saludo."
    )
