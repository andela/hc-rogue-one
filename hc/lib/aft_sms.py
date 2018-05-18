from africastalking.AfricasTalkingGateway import AfricasTalkingGateway, AfricasTalkingGatewayException

from hc.front.templatetags.hc_extras import hc_duration


class AfricasTalkingSMS(object):
    def __init__(self, username, api_key):
        self.gateway = AfricasTalkingGateway(username, api_key)

    def send(self, recipients, message):
        try:
            self.gateway.sendMessage(recipients, message)

        except AfricasTalkingGatewayException as e:
            return 'Encountered an error while sending: %s' % str(e)


def send_sms(ctx):
    check = ctx.get('check', None)
    channel = ctx.get('channel', None)
    dtfmt = "%Y-%m-%d %H:%M"

    if check and channel:
        username, api_key, recipients = channel.africas_talking_username, channel.africas_talking_api_key, channel.value
        message = """
HEALTH-CHECKS ALERT!!
        Name: %(name)s\n
        Status: %(status)s\n
        Period: %(period)s\n
        Last Ping: %(l_ping)s\n
        Total Pings: %(t_ping)s\n
        """ % dict(name=check.name_then_code(),
                   status=check.status,
                   period=hc_duration(check.timeout),
                   l_ping=check.last_ping.strftime(dtfmt),
                   t_ping=check.n_pings)
        instance = AfricasTalkingSMS(username, api_key)
        return instance.send(recipients, message)