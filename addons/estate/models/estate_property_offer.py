from odoo import api, fields, models
from odoo.exceptions import UserError
from datetime import timedelta


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float()
    status = fields.Selection(
        selection=[
            ('accepted', 'Accepted'),
            ('refused', 'Refused'),
        ],
        copy=False
    )
    partner_id = fields.Many2one("res.partner", required=True)
    property_id = fields.Many2one("estate.property", required=True)
    validity = fields.Integer("validity (days)", default=7)
    date_deadline = fields.Date(compute="_compute_date_deadline", inverse="_inverse_date_deadline", string="Deadline")
    property_state = fields.Selection(related="property_id.state", readonly=True)
    property_type_id = fields.Many2one(related="property_id.property_type_id", store=True)

    _sql_constraints = [
        ('check_offer_price_positive', 'CHECK(price > 0)',
         'The offer price must be strictly positive.'),
    ]

    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            if record.create_date:
                record.date_deadline = record.create_date + timedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + timedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if record.date_deadline and record.create_date:
                delta = record.date_deadline - record.create_date.date()
                record.validity = delta.days
            else:
                record.validity = (record.date_deadline - fields.Date.today()).days

    def action_accept(self):
        for record in self:
            if record.property_id.state == "sold":
                raise UserError("Cannot accept offer for a sold property.")
            record.status = "accepted"
            record.property_id.buyer_id = record.partner_id
            record.property_id.selling_price = record.price
        return True


    def action_refuse(self):
        for record in self:
            record.status = "refused"
        return True

    @api.model
    def create(self, vals):
        existing_offers = self.search([("property_id", "=", vals["property_id"])])
        for offer in existing_offers:
            if vals["price"] <= offer.price:
                raise UserError("The offer amount must be higher than existing offers.")
        property = self.env["estate.property"].browse(vals["property_id"])
        property.state = "offer_received"
        return super(EstatePropertyOffer, self).create(vals)