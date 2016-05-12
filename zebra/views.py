import json
import logging

import stripe
from django.apps import apps
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from zebra.conf import options
from zebra.signals import *

log = logging.getLogger("zebra.{0}".format(__name__))

stripe.api_key = options.STRIPE_SECRET


def _try_to_get_customer_from_customer_id(stripe_customer_id):
    if options.ZEBRA_CUSTOMER_MODEL:
        m = apps.get_model(*options.ZEBRA_CUSTOMER_MODEL.split('.'))
        try:
            return m.objects.get(stripe_customer_id=stripe_customer_id)
        except:
            pass
    return None


@csrf_exempt
def webhooks(request):
    """
    Handles all known webhooks from stripe, and calls signals.
    Plug in as you need.
    """

    if request.method != "POST":
        return HttpResponse("Invalid Request.", status=400)

    request_data = json.loads(request.POST["request_data"])

    if request_data["event"] == "recurring_payment_failed":
        zebra_webhook_recurring_payment_failed.send(
            sender=None,
            customer=_try_to_get_customer_from_customer_id(request_data["customer"]),
            full_request_data=request_data)

    elif request_data["event"] == "invoice_ready":
        zebra_webhook_invoice_ready.send(
            sender=None,
            customer=_try_to_get_customer_from_customer_id(request_data["customer"]),
            full_request_data=request_data)

    elif request_data["event"] == "recurring_payment_succeeded":
        zebra_webhook_recurring_payment_succeeded.send(
            sender=None,
            customer=_try_to_get_customer_from_customer_id(request_data["customer"]),
            full_request_data=request_data)

    elif request_data["event"] == "subscription_trial_ending":
        zebra_webhook_subscription_trial_ending.send(
            sender=None,
            customer=_try_to_get_customer_from_customer_id(request_data["customer"]),
            full_request_data=request_data)

    elif request_data["event"] == "subscription_final_payment_attempt_failed":
        zebra_webhook_subscription_final_payment_attempt_failed.send(
            sender=None,
            customer=_try_to_get_customer_from_customer_id(request_data["customer"]),
            full_request_data=request_data)

    elif request_data["event"] == "ping":
        zebra_webhook_subscription_ping_sent.send(sender=None)

    else:
        return HttpResponse(status=400)

    return HttpResponse(status=200)


@csrf_exempt
def webhooks_v2(request):
    """
    Handles all known webhooks from stripe, and calls signals.
    Plug in as you need.
    """
    if request.method != "POST":
        return HttpResponse("Invalid Request.", status=400)

    event_json = json.loads(request.body)
    event_key = event_json['type'].replace('.', '_')

    if event_key in WEBHOOK_MAP:
        WEBHOOK_MAP[event_key].send(sender=None, full_json=event_json)

    return HttpResponse(status=200)
