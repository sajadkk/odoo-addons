openerp.listview_monetary = function(instance) {
    instance.web.list.columns.add('field.monetary','instance.web.list.FieldMonetary');

    instance.web.list.FieldMonetary = instance.web.list.Column.extend({
        /**
         * Return amount with currency symbol
         *
         * @private
         */
        init: function() {
            this._super.apply(this, arguments);
            this.cur_map = {
                "ALL": "L"
                , "AED": "د.إ"
                , "AFN": "؋"
                , "ARS": "$"
                , "AWG": "ƒ"
                , "AUD": "$"
                , "AZN": "m"
                , "BSD": "$"
                , "BBD": "$"
                , "BYR": "p."
                , "BZD": "BZ$"
                , "BMD": "$"
                , "BOB": "Bs."
                , "BAM": "KM"
                , "BWP": "P"
                , "BGN": "лв"
                , "BRL": "R$"
                , "BND": "$"
                , "KHR": "៛"
                , "CAD": "$"
                , "KYD": "$"
                , "CLP": "$"
                , "CNY": "¥"
                , "COP": "$"
                , "CRC": "₡"
                , "HRK": "kn"
                , "CUP": "₱"
                , "CZK": "Kč"
                , "DKK": "kr"
                , "DOP": "RD$"
                , "XCD": "$"
                , "EGP": "£"
                , "SVC": "$"
                , "EEK": "kr"
                , "EUR": "€"
                , "FKP": "£"
                , "FJD": "$"
                , "GHC": "¢"
                , "GIP": "£"
                , "GTQ": "Q"
                , "GGP": "£"
                , "GYD": "$"
                , "HNL": "L"
                , "HKD": "$"
                , "HUF": "Ft"
                , "ISK": "kr"
                , "INR": "₹"
                , "IDR": "Rp"
                , "IRR": "﷼"
                , "IMP": "£"
                , "ILS": "₪"
                , "JMD": "J$"
                , "JPY": "¥"
                , "JEP": "£"
                , "KES": "KSh"
                , "KZT": "лв"
                , "KPW": "₩"
                , "KRW": "₩"
                , "KGS": "лв"
                , "LAK": "₭"
                , "LVL": "Ls"
                , "LBP": "£"
                , "LRD": "$"
                , "LTL": "Lt"
                , "MKD": "ден"
                , "MYR": "RM"
                , "MUR": "₨"
                , "MXN": "$"
                , "MNT": "₮"
                , "MZN": "MT"
                , "NAD": "$"
                , "NPR": "₨"
                , "ANG": "ƒ"
                , "NZD": "$"
                , "NIO": "C$"
                , "NGN": "₦"
                , "NOK": "kr"
                , "OMR": "﷼"
                , "PKR": "₨"
                , "PAB": "B/."
                , "PYG": "Gs"
                , "PEN": "S/."
                , "PHP": "₱"
                , "PLN": "zł"
                , "QAR": "﷼"
                , "RON": "lei"
                , "RUB": "₽"
                , "SHP": "£"
                , "SAR": "﷼"
                , "RSD": "Дин."
                , "SCR": "₨"
                , "SGD": "$"
                , "SBD": "$"
                , "SOS": "S"
                , "ZAR": "R"
                , "LKR": "₨"
                , "SEK": "kr"
                , "CHF": "Fr."
                , "SRD": "$"
                , "SYP": "£"
                , "TZS": "TSh"
                , "TWD": "NT$"
                , "THB": "฿"
                , "TTD": "TT$"
                , "TRY": ""
                , "TRL": "₤"
                , "TVD": "$"
                , "UGX": "USh"
                , "UAH": "₴"
                , "GBP": "£"
                , "USD": "$"
                , "UYU": "$U"
                , "UZS": "лв"
                , "VEF": "Bs"
                , "VND": "₫"
                , "YER": "﷼"
                , "ZWD": "Z$"
                };
        },
        _format: function (row_data, options) {
            var self = this;
            var fm = new instance.web.form.DefaultFieldManager(this);
            this.fm = fm;
            console.log(fm.get_field_value('currency_id'));
            if (this.type == "float") {
                if (row_data.currency_id) {
                    var symbol = "";
                    if(self.cur_map[row_data.currency_id.value[1]]!==undefined) {
                        symbol = self.cur_map[row_data.currency_id.value[1]]
                    }
                    var amount = _.escape(instance.web.format_value(row_data[this.id].value, {'type': 'float'}));
                    return _.template('<span><%-symbol%><%-amount%></span>', {'amount': amount, 'symbol': symbol});
                }
                return _.escape(instance.web.format_value(row_data[this.id].value, {'type': 'float'}, options.value_if_empty));
            }
        }
    });
};