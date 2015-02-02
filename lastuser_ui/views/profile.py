# -*- coding: utf-8 -*-

import json

from flask import g, flash, render_template, url_for, request
from coaster.views import load_model
from baseframe import _
from baseframe.forms import render_form, render_redirect, render_delete_sqla

from lastuser_core import login_registry
from lastuser_core.models import db, UserEmail, UserEmailClaim, UserPhone, UserPhoneClaim
from lastuser_core.signals import user_data_changed
from lastuser_oauth.mailclient import send_email_verify_link
from lastuser_oauth.views.helpers import requires_login
from lastuser_oauth.forms import PasswordResetForm, PasswordChangeForm
from .. import lastuser_ui
from ..forms import NewEmailAddressForm, NewPhoneForm, VerifyPhoneForm
from .sms import send_phone_verify_code


@lastuser_ui.route('/profile')
@requires_login
def profile():
    email_form = NewEmailAddressForm()
    phone_form = NewPhoneForm()
    context = {
        'login_registry': login_registry,

        #Email Form
        'email_form': email_form,
        'email_form_id': 'email_form',
        'email_form_submit': _("Add Email"),
        'email_form_action': url_for('.email_json'),

        #Phone Form
        'phone_form': phone_form,
        'phone_form_id': 'phone_form',
        'phone_form_submit': _("Add Phone"),
        'phone_form_action': url_for('.phone_json')
    }
    return render_template('profile.html', context=context)


@lastuser_ui.route('/profile/password', methods=['GET', 'POST'])
@requires_login
def change_password():
    if not g.user.pw_hash:
        form = PasswordResetForm()
        form.edit_user = g.user
        del form.username
    else:
        form = PasswordChangeForm()
        form.edit_user = g.user
    if form.validate_on_submit():
        g.user.password = form.password.data
        db.session.commit()
        flash(_("Your new password has been saved"), category='success')
        return render_redirect(url_for('.profile'), code=303)
    return render_form(form=form, title=_("Change password"), formid='changepassword',
        submit=_("Change password"), ajax=True)


@lastuser_ui.route('/profile/email/json', methods=['GET', 'POST'])
@requires_login
def email_json():
    form = NewEmailAddressForm()
    response = {
        'errors': [],
        'modal': ''
    }
    if form.validate_on_submit():
        useremail = UserEmailClaim.get(user=g.user, email=form.email.data)
        if useremail is None:
            useremail = UserEmailClaim(user=g.user, email=form.email.data, type=form.type.data)
            db.session.add(useremail)
            db.session.commit()
        send_email_verify_link(useremail)
        response.update({
            'modal': _("We sent you an email to confirm your address")
        })
        user_data_changed.send(g.user, changes=['email-claim'])
        return json.dumps(response)
    response.update({
        'errors': [{key: form.errors[key]} for key in form.errors]
    })
    return json.dumps(response)


@lastuser_ui.route('/profile/phone/json', methods=['GET', 'POST'])
@requires_login
def phone_json():
    form = NewPhoneForm()
    response = {
        'errors': [],
        'modal': ''
    }
    if form.validate_on_submit():
        userphone = UserPhoneClaim.get(user=g.user, phone=form.phone.data)
        if userphone is None:
            userphone = UserPhoneClaim(user=g.user, phone=form.phone.data, type=form.type.data)
            db.session.add(userphone)
        send_phone_verify_code(userphone)
        db.session.commit()  # Commit after sending because send_phone_verify_code saves the message sent
        response.update({
            'modal': _("We sent you a verification code to your phone")
        })
        user_data_changed.send(g.user, changes=['phone-claim'])
        return json.dumps(response)
    response.update({
        'errors': json.dumps(form.errors)
    })
    return json.dumps(response)


@lastuser_ui.route('/profile/email/new', methods=['GET', 'POST'])
@requires_login
def add_email():
    form = NewEmailAddressForm()
    if form.validate_on_submit():
        useremail = UserEmailClaim.get(user=g.user, email=form.email.data)
        if useremail is None:
            useremail = UserEmailClaim(user=g.user, email=form.email.data, type=form.type.data)
            db.session.add(useremail)
            db.session.commit()
        send_email_verify_link(useremail)
        flash(_("We sent you an email to confirm your address"), 'success')
        user_data_changed.send(g.user, changes=['email-claim'])
        return render_redirect(url_for('.profile'), code=303)
    return render_form(form=form, title=_("Add an email address"), formid='email_add',
        submit=_("Add email"), ajax=True)


@lastuser_ui.route('/profile/email/<md5sum>/remove', methods=['GET', 'POST'])
@requires_login
def remove_email(md5sum):
    useremail = UserEmail.query.filter_by(md5sum=md5sum, user=g.user).first()
    if not useremail:
        useremail = UserEmailClaim.query.filter_by(md5sum=md5sum, user=g.user).first_or_404()
    if isinstance(useremail, UserEmail) and useremail.primary:
        flash(_("You cannot remove your primary email address"), 'error')
        return render_redirect(url_for('.profile'), code=303)
    if request.method == 'POST':
        # FIXME: Confirm validation success
        user_data_changed.send(g.user, changes=['email-delete'])
    return render_delete_sqla(useremail, db, title=_(u"Confirm removal"),
        message=_(u"Remove email address {email}?").format(
            email=useremail.email),
        success=_(u"You have removed your email address {email}").format(email=useremail.email),
        next=url_for('.profile'))


@lastuser_ui.route('/profile/phone/new', methods=['GET', 'POST'])
@requires_login
def add_phone():
    form = NewPhoneForm()
    if form.validate_on_submit():
        userphone = UserPhoneClaim.get(user=g.user, phone=form.phone.data)
        if userphone is None:
            userphone = UserPhoneClaim(user=g.user, phone=form.phone.data, type=form.type.data)
            db.session.add(userphone)
        send_phone_verify_code(userphone)
        db.session.commit()  # Commit after sending because send_phone_verify_code saves the message sent
        flash(_("We sent a verification code to your phone number"), 'success')
        user_data_changed.send(g.user, changes=['phone-claim'])
        return render_redirect(url_for('.verify_phone', number=userphone.phone), code=303)
    return render_form(form=form, title=_("Add a phone number"), formid='phone_add',
        submit=_("Add phone"), ajax=True)


@lastuser_ui.route('/profile/phone/<number>/remove', methods=['GET', 'POST'])
@requires_login
def remove_phone(number):
    userphone = UserPhone.query.filter_by(phone=number, user=g.user).first()
    if userphone is None:
        userphone = UserPhoneClaim.query.filter_by(phone=number, user=g.user).first_or_404()
    if request.method == 'POST':
        # FIXME: Confirm validation success
        user_data_changed.send(g.user, changes=['phone-delete'])
    return render_delete_sqla(userphone, db, title=_(u"Confirm removal"),
        message=_(u"Remove phone number {phone}?").format(
            phone=userphone.phone),
        success=_(u"You have removed your number {phone}").format(phone=userphone.phone),
        next=url_for('.profile'))


@lastuser_ui.route('/profile/phone/<number>/verify', methods=['GET', 'POST'])
@requires_login
@load_model(UserPhoneClaim, {'phone': 'number'}, 'phoneclaim', permission='verify')
def verify_phone(phoneclaim):
    form = VerifyPhoneForm()
    form.phoneclaim = phoneclaim
    if form.validate_on_submit():
        if UserPhone.get(phoneclaim.phone) is None:
            if not g.user.phones:
                primary = True
            else:
                primary = False
            userphone = UserPhone(user=g.user, phone=phoneclaim.phone, gets_text=True, primary=primary)
            db.session.add(userphone)
            db.session.delete(phoneclaim)
            db.session.commit()
            flash(_("Your phone number has been verified"), 'success')
            user_data_changed.send(g.user, changes=['phone'])
            return render_redirect(url_for('.profile'), code=303)
        else:
            db.session.delete(phoneclaim)
            db.session.commit()
            flash(_("This phone number has already been claimed by another user"), 'danger')
    return render_form(form=form, title=_("Verify phone number"), formid='phone_verify',
        submit=_("Verify"), ajax=True)
