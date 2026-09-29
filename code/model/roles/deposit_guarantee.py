from model.base import EcoRole


class DepositGuarantee(EcoRole):

    #
    # Perceptions
    #
    def find_defaults(self):
        env = self.env
        defaults = []
        for role in env.find_all_roles("deposit_demander"):
            if not role.defaulted:
                continue
            amount = env.get_stock("deposits", role.id)
            default = dict(bank=role, amount=amount)
            defaults.append(default)
        return defaults

    def find_deposits(self, deposit_demander):
        return self.env.find_links(deposit_demander, "deposit_supplier")

    #
    # Actions
    #
    def reimburse_deposits(self, deposit_supplier, amount):
        self.env.reimburse_deposits(self, deposit_supplier, amount)
