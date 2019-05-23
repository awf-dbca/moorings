from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.conf import settings
from django.core.exceptions import ValidationError

from datetime import datetime, timedelta
from commercialoperator.components.main.models import Park
from ledger.checkout.utils import create_basket_session, create_checkout_session
import json
from decimal import Decimal

from commercialoperator.components.bookings.models import Booking, ParkBooking

import logging
logger = logging.getLogger('payment_checkout')


def create_booking(request, proposal_id):
    """ Create the ledger lines - line items for invoice sent to payment system """

    #import ipdb; ipdb.set_trace()
    booking = Booking.objects.create(proposal_id=proposal_id)

    tbody = json.loads(request.POST['payment'])['tbody']
    for row in tbody:
        park_id = row[0]['value']
        arrival = row[1]
        no_adults = int(row[2]) if row[2] else 0
        no_children = int(row[3]) if row[3] else 0
        no_free_of_charge = int(row[4]) if row[4] else 0
        park = Park.objects.get(id=park_id)

        if any([no_adults, no_children, no_free_of_charge]) > 0:
            park_booking = ParkBooking.objects.create(
                booking = booking,
                park_id = park_id,
                arrival = datetime.strptime(arrival, '%Y-%m-%d').date(),
                no_adults = no_adults,
                no_children = no_children,
                no_free_of_charge = no_free_of_charge,
                cost = no_adults*park.adult_price + no_children*park.child_price
            )
    if not park_booking:
        raise ValidationError('Must have at least one person visiting the park')

    return booking


def get_session_booking(session):
    if 'cols_booking' in session:
        booking_id = session['cols_booking']
    else:
        raise Exception('Booking not in Session')

    try:
        return Booking.objects.get(id=booking_id)
    except Booking.DoesNotExist:
        raise Exception('Booking not found for booking_id {}'.format(booking_id))


def set_session_booking(session, booking):
    session['cols_booking'] = booking.id
    session.modified = True

def delete_session_booking(session):
    if 'cols_booking' in session:
        del session['cols_booking']
        session.modified = True

def create_fee_lines(proposal, invoice_text=None, vouchers=[], internal=False):
    """ Create the ledger lines - line item for application fee sent to payment system """

    #import ipdb; ipdb.set_trace()
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    return [{
            'ledger_description': 'Proposal Application Fee - {} - {}'.format(now, proposal.lodgement_number),
            'oracle_code': proposal.application_type.oracle_code,
            'price_incl_tax':  proposal.application_type.application_fee,
            'quantity': 1
        }]

def create_lines(request, invoice_text=None, vouchers=[], internal=False):
    """ Create the ledger lines - line items for invoice sent to payment system """

    #import ipdb; ipdb.set_trace()
    def add_line_item(park_name, arrival, oracle_code, age_group, price, no_persons):
        if no_persons > 0:
            return {
                'ledger_description': '{} - {} - {}'.format(park_name, arrival, age_group),
                'oracle_code': oracle_code,
                'price_incl_tax':  Decimal(price),
                'quantity': no_persons,
            }
        return None

    lines = []
    tbody = json.loads(request.POST['payment'])['tbody']
    for row in tbody:
        park_id = row[0]['value']
        arrival = row[1]
        no_adults = int(row[2]) if row[2] else 0
        no_children = int(row[3]) if row[3] else 0
        no_free_of_charge = int(row[4]) if row[4] else 0
        park= Park.objects.get(id=park_id)
        oracle_code = 'ABC123 GST'

        if no_adults > 0:
            lines.append(add_line_item(park.name, arrival, oracle_code, 'Adult', price=park.adult_price, no_persons=no_adults))

        if no_children > 0:
            lines.append(add_line_item(park.name, arrival, oracle_code, 'Child', price=park.child_price, no_persons=no_children))

        if no_free_of_charge > 0:
            lines.append(add_line_item(park.name, arrival, oracle_code, 'Free', price=0.0, no_persons=no_free_of_charge))

    return lines

def checkout(request, proposal, lines, invoice_text=None, vouchers=[], internal=False):
    #import ipdb; ipdb.set_trace()
    basket_params = {
        'products': lines,
        'vouchers': vouchers,
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'custom_basket': True,
    }

    basket, basket_hash = create_basket_session(request, basket_params)
    #fallback_url = request.build_absolute_uri('/')
    checkout_params = {
        'system': settings.PS_PAYMENT_SYSTEM_ID,
        'fallback_url': request.build_absolute_uri('/'),                                      # 'http://mooring-ria-jm.dbca.wa.gov.au/'
        'return_url': request.build_absolute_uri(reverse('public_booking_success')),          # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        'return_preload_url': request.build_absolute_uri(reverse('public_booking_success')),  # 'http://mooring-ria-jm.dbca.wa.gov.au/success/'
        #'fallback_url': fallback_url,
        #'return_url': fallback_url,
        #'return_preload_url': fallback_url,
        'force_redirect': True,
        'proxy': True if internal else False,
        'invoice_text': invoice_text,                                                         # 'Reservation for Jawaid Mushtaq from 2019-05-17 to 2019-05-19 at RIA 005'
    }
#    if not internal:
#        checkout_params['check_url'] = request.build_absolute_uri('/api/booking/{}/booking_checkout_status.json'.format(booking.id))
    if internal or request.user.is_anonymous():
        #checkout_params['basket_owner'] = booking.customer.id
        checkout_params['basket_owner'] = proposal.submitter_id


    create_checkout_session(request, checkout_params)

#    if internal:
#        response = place_order_submission(request)
#    else:
    response = HttpResponseRedirect(reverse('checkout:index'))
    # inject the current basket into the redirect response cookies
    # or else, anonymous users will be directionless
    response.set_cookie(
            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
    )

#    if booking.cost_total < 0:
#        response = HttpResponseRedirect('/refund-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )
#
#    # Zero booking costs
#    if booking.cost_total < 1 and booking.cost_total > -1:
#        response = HttpResponseRedirect('/no-payment')
#        response.set_cookie(
#            settings.OSCAR_BASKET_COOKIE_OPEN, basket_hash,
#            max_age=settings.OSCAR_BASKET_COOKIE_LIFETIME,
#            secure=settings.OSCAR_BASKET_COOKIE_SECURE, httponly=True
#        )

    return response


