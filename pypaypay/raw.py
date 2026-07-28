"""Auto-generated raw API surface for pypaypay.

Every method is a thin wrapper around a single PayPay BFF endpoint.
Parameter names come from the decompiled Android app; pass None to omit.
Additional fields can be supplied via ``**extra``.

DO NOT EDIT — regenerate with scripts/codegen if the app is updated.
"""
from __future__ import annotations
from typing import Any, Dict, Optional


class RawAPI:
    """Thin 1:1 wrapper over every discovered BFF endpoint.

    Bound to a PayPay client via ``pp.raw``. Each method returns the
    parsed ``payload`` dict from the BFF response.
    """

    def __init__(self, client) -> None:
        self._c = client

    def accept_p2p_request_money(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/acceptP2PRequestMoney``
                Body is a typed ``UserDefinedLimitInfoDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/acceptP2PRequestMoney', json=body)

    def accept_p2p_send_money(self, *, channelUrl: Optional[Any] = None, messageId: Optional[Any] = None, orderId: Optional[Any] = None, requestId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/acceptP2PSendMoney``
                Body: channelUrl, messageId, orderId, requestId
        """
        body: Dict[str, Any] = {}
        if channelUrl is not None: body['channelUrl'] = channelUrl
        if messageId is not None: body['messageId'] = messageId
        if orderId is not None: body['orderId'] = orderId
        if requestId is not None: body['requestId'] = requestId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/acceptP2PSendMoney', json=body)

    def agree_similar_transaction(self, *, paymentCodeSessionId: Optional[Any] = None, agreeSimilarTransactionFlag: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/agreeSimilarTransaction``
                Body: paymentCodeSessionId, agreeSimilarTransactionFlag
        """
        body: Dict[str, Any] = {}
        if paymentCodeSessionId is not None: body['paymentCodeSessionId'] = paymentCodeSessionId
        if agreeSimilarTransactionFlag is not None: body['agreeSimilarTransactionFlag'] = agreeSimilarTransactionFlag
        body.update(extra)
        return self._c._request("POST", 'bff/v1/agreeSimilarTransaction', json=body)

    def agree_to_privacy_policy(self, *, version: Optional[Any] = None, autoAcceptTermsOfUse: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/agreeToPrivacyPolicy``
                Body: version, autoAcceptTermsOfUse
        """
        body: Dict[str, Any] = {}
        if version is not None: body['version'] = version
        if autoAcceptTermsOfUse is not None: body['autoAcceptTermsOfUse'] = autoAcceptTermsOfUse
        body.update(extra)
        return self._c._request("POST", 'bff/v1/agreeToPrivacyPolicy', json=body)

    def authorize_password(self, *, type: Optional[Any] = None, password: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/authorizePassword``
                Body: type, password
        """
        body: Dict[str, Any] = {}
        if type is not None: body['type'] = type
        if password is not None: body['password'] = password
        body.update(extra)
        return self._c._request("POST", 'bff/v1/authorizePassword', json=body)

    def calculate_myna_send_apply_info(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/calculateMynaSendApplyInfo``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/calculateMynaSendApplyInfo', json=body)

    def cancel_p2p_request_money(self, *, channelUrl: Optional[Any] = None, messageId: Optional[Any] = None, requestId: Optional[Any] = None, requestMoneyId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/cancelP2PRequestMoney``
                Body: channelUrl, messageId, requestId, requestMoneyId
        """
        body: Dict[str, Any] = {}
        if channelUrl is not None: body['channelUrl'] = channelUrl
        if messageId is not None: body['messageId'] = messageId
        if requestId is not None: body['requestId'] = requestId
        if requestMoneyId is not None: body['requestMoneyId'] = requestMoneyId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/cancelP2PRequestMoney', json=body)

    def cancel_p2p_send_money(self, *, channelUrl: Optional[Any] = None, messageId: Optional[Any] = None, orderId: Optional[Any] = None, requestId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/cancelP2PSendMoney``
                Body: channelUrl, messageId, orderId, requestId
        """
        body: Dict[str, Any] = {}
        if channelUrl is not None: body['channelUrl'] = channelUrl
        if messageId is not None: body['messageId'] = messageId
        if orderId is not None: body['orderId'] = orderId
        if requestId is not None: body['requestId'] = requestId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/cancelP2PSendMoney', json=body)

    def change_avatar_image(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/changeAvatarImage``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/changeAvatarImage', json=body)

    def change_payment_method_state(self, *, paymentMethodId: Optional[Any] = None, state: Optional[Any] = None, paymentMethodType: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/changePaymentMethodState``
                Body: paymentMethodId, state, paymentMethodType
        """
        body: Dict[str, Any] = {}
        if paymentMethodId is not None: body['paymentMethodId'] = paymentMethodId
        if state is not None: body['state'] = state
        if paymentMethodType is not None: body['paymentMethodType'] = paymentMethodType
        body.update(extra)
        return self._c._request("POST", 'bff/v1/changePaymentMethodState', json=body)

    def change_searchable_paypay_id(self, *, searchablePayPayId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/changeSearchablePayPayId``
                Body: searchablePayPayId
        """
        body: Dict[str, Any] = {}
        if searchablePayPayId is not None: body['searchablePayPayId'] = searchablePayPayId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/changeSearchablePayPayId', json=body)

    def change_searchable_phone_number(self, *, searchablePhoneNumber: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/changeSearchablePhoneNumber``
                Body: searchablePhoneNumber
        """
        body: Dict[str, Any] = {}
        if searchablePhoneNumber is not None: body['searchablePhoneNumber'] = searchablePhoneNumber
        body.update(extra)
        return self._c._request("POST", 'bff/v1/changeSearchablePhoneNumber', json=body)

    def change_user_profile(self, *, nickName: Optional[Any] = None, firstName: Optional[Any] = None, lastName: Optional[Any] = None, firstNameKana: Optional[Any] = None, lastNameKana: Optional[Any] = None, firstNameRomaji: Optional[Any] = None, lastNameRomaji: Optional[Any] = None, dateOfBirth: Optional[Any] = None, gender: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/changeUserProfile``
                Body: nickName, firstName, lastName, firstNameKana, lastNameKana, firstNameRomaji, lastNameRomaji, dateOfBirth, gender
        """
        body: Dict[str, Any] = {}
        if nickName is not None: body['nickName'] = nickName
        if firstName is not None: body['firstName'] = firstName
        if lastName is not None: body['lastName'] = lastName
        if firstNameKana is not None: body['firstNameKana'] = firstNameKana
        if lastNameKana is not None: body['lastNameKana'] = lastNameKana
        if firstNameRomaji is not None: body['firstNameRomaji'] = firstNameRomaji
        if lastNameRomaji is not None: body['lastNameRomaji'] = lastNameRomaji
        if dateOfBirth is not None: body['dateOfBirth'] = dateOfBirth
        if gender is not None: body['gender'] = gender
        body.update(extra)
        return self._c._request("POST", 'bff/v1/changeUserProfile', json=body)

    def change_yconnect(self, *, sessionId: Optional[Any] = None, state: Optional[Any] = None, code: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/changeYconnect``
                Body: sessionId, state, code
        """
        body: Dict[str, Any] = {}
        if sessionId is not None: body['sessionId'] = sessionId
        if state is not None: body['state'] = state
        if code is not None: body['code'] = code
        body.update(extra)
        return self._c._request("POST", 'bff/v1/changeYconnect', json=body)

    def check_auth_action_for_user_defined_limit_update(self, *, mode: Optional[Any] = None, dailyLimit: Optional[Any] = None, monthlyLimit: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/checkAuthActionForUserDefinedLimitUpdate``
                Body: mode, dailyLimit, monthlyLimit
        """
        body: Dict[str, Any] = {}
        if mode is not None: body['mode'] = mode
        if dailyLimit is not None: body['dailyLimit'] = dailyLimit
        if monthlyLimit is not None: body['monthlyLimit'] = monthlyLimit
        body.update(extra)
        return self._c._request("POST", 'bff/v1/checkAuthActionForUserDefinedLimitUpdate', json=body)

    def confirm_age_for_cashback(self, *, year: Optional[Any] = None, month: Optional[Any] = None, date: Optional[Any] = None, orderId: Optional[Any] = None, orderType: Optional[Any] = None, campaignId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/confirmAgeForCashback``
                Body: year, month, date, orderId, orderType, campaignId
        """
        body: Dict[str, Any] = {}
        if year is not None: body['year'] = year
        if month is not None: body['month'] = month
        if date is not None: body['date'] = date
        if orderId is not None: body['orderId'] = orderId
        if orderType is not None: body['orderType'] = orderType
        if campaignId is not None: body['campaignId'] = campaignId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/confirmAgeForCashback', json=body)

    def create_offline_one_time_code_config(self, *, userIdentitiesToken: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/createOfflineOneTimeCodeConfig``
                Body: userIdentitiesToken
        """
        body: Dict[str, Any] = {}
        if userIdentitiesToken is not None: body['userIdentitiesToken'] = userIdentitiesToken
        body.update(extra)
        return self._c._request("POST", 'bff/v1/createOfflineOneTimeCodeConfig', json=body)

    def create_p2p_code(self, *, sessionId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/createP2PCode``
                Body: sessionId
        """
        body: Dict[str, Any] = {}
        if sessionId is not None: body['sessionId'] = sessionId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/createP2PCode', json=body)

    def create_p2p_user_search_history(self, *, searchTerm: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/createP2PUserSearchHistory``
                Body: searchTerm
        """
        body: Dict[str, Any] = {}
        if searchTerm is not None: body['searchTerm'] = searchTerm
        body.update(extra)
        return self._c._request("POST", 'bff/v1/createP2PUserSearchHistory', json=body)

    def create_paypay_sign_in_code(self, *, clientId: Optional[Any] = None, redirectUrl: Optional[Any] = None, scope: Optional[Any] = None, state: Optional[Any] = None, approved: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/createPayPaySignInCode``
                Body: clientId, redirectUrl, scope, state, approved
        """
        body: Dict[str, Any] = {}
        if clientId is not None: body['clientId'] = clientId
        if redirectUrl is not None: body['redirectUrl'] = redirectUrl
        if scope is not None: body['scope'] = scope
        if state is not None: body['state'] = state
        if approved is not None: body['approved'] = approved
        body.update(extra)
        return self._c._request("POST", 'bff/v1/createPayPaySignInCode', json=body)

    def delete_notification_thread(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/deleteNotificationThread``
                Body is a typed ``DeleteNotificationThreadParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/deleteNotificationThread', json=body)

    def delete_p2p_user_search_history(self, *, deleteSearchStatus: Optional[Any] = None, searchTerm: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/deleteP2PUserSearchHistory``
                Body: deleteSearchStatus, searchTerm
                Query: deleteSearchStatus
        """
        body: Dict[str, Any] = {}
        if deleteSearchStatus is not None: body['deleteSearchStatus'] = deleteSearchStatus
        if searchTerm is not None: body['searchTerm'] = searchTerm
        body.update(extra)
        params: Dict[str, Any] = {}
        if deleteSearchStatus is not None: params['deleteSearchStatus'] = deleteSearchStatus
        return self._c._request("POST", 'bff/v1/deleteP2PUserSearchHistory', json=body, params=params or None)

    def delete_payment_method(self, *, paymentMethodId: Optional[Any] = None, paymentMethodType: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/deletePaymentMethod``
                Body: paymentMethodId, paymentMethodType
        """
        body: Dict[str, Any] = {}
        if paymentMethodId is not None: body['paymentMethodId'] = paymentMethodId
        if paymentMethodType is not None: body['paymentMethodType'] = paymentMethodType
        body.update(extra)
        return self._c._request("POST", 'bff/v1/deletePaymentMethod', json=body)

    def delete_payout_method(self, *, payoutMethodId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/deletePayoutMethod``
                Body: payoutMethodId
        """
        body: Dict[str, Any] = {}
        if payoutMethodId is not None: body['payoutMethodId'] = payoutMethodId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/deletePayoutMethod', json=body)

    def delete_temporary_mail_address(self, *, externalProvider: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/deleteTemporaryMailAddress``
                Body: externalProvider
        """
        body: Dict[str, Any] = {}
        if externalProvider is not None: body['externalProvider'] = externalProvider
        body.update(extra)
        return self._c._request("POST", 'bff/v1/deleteTemporaryMailAddress', json=body)

    def follow_channel(self, *, channelId: Optional[Any] = None, type: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/followChannel``
                Body: channelId, type
        """
        body: Dict[str, Any] = {}
        if channelId is not None: body['channelId'] = channelId
        if type is not None: body['type'] = type
        body.update(extra)
        return self._c._request("POST", 'bff/v1/followChannel', json=body)

    def get_atm_topup_display_info(self, *, requestId: Optional[Any] = None, code: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getATMTopupDisplayInfo``
                Query: requestId, code
        """
        params: Dict[str, Any] = {}
        if requestId is not None: params['requestId'] = requestId
        if code is not None: params['code'] = code
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getATMTopupDisplayInfo', params=params)

    def get_address_by_zipcode(self, *, zipcode: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getAddressByZipcode``
                Query: zipcode
        """
        params: Dict[str, Any] = {}
        if zipcode is not None: params['zipcode'] = zipcode
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getAddressByZipcode', params=params)

    def get_balance_info(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/getBalanceInfo``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/getBalanceInfo', json=body)

    def get_channel_display_info(self, *, lat: Optional[Any] = None, lon: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getChannelDisplayInfo``
                Query: lat, lon
        """
        params: Dict[str, Any] = {}
        if lat is not None: params['lat'] = lat
        if lon is not None: params['lon'] = lon
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getChannelDisplayInfo', params=params)

    def get_continuous_payment_display_info(self, *, continuousPaymentId: Optional[Any] = None, paymentMethodId: Optional[Any] = None, paymentMethodType: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getContinuousPaymentDisplayInfo``
                Query: continuousPaymentId, paymentMethodId, paymentMethodType
        """
        params: Dict[str, Any] = {}
        if continuousPaymentId is not None: params['continuousPaymentId'] = continuousPaymentId
        if paymentMethodId is not None: params['paymentMethodId'] = paymentMethodId
        if paymentMethodType is not None: params['paymentMethodType'] = paymentMethodType
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getContinuousPaymentDisplayInfo', params=params)

    def get_credit_card_registration_failure(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getCreditCardRegistrationFailure``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getCreditCardRegistrationFailure', params=params or None)

    def get_feed_list(self, *, type: Optional[Any] = None, pageNumber: Optional[Any] = None, lat: Optional[Any] = None, lon: Optional[Any] = None, id: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getFeedList``
                Query: type, pageNumber, lat, lon, id
        """
        params: Dict[str, Any] = {}
        if type is not None: params['type'] = type
        if pageNumber is not None: params['pageNumber'] = pageNumber
        if lat is not None: params['lat'] = lat
        if lon is not None: params['lon'] = lon
        if id is not None: params['id'] = id
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getFeedList', params=params)

    def get_gv_list(self, *, statusFilter: Optional[Any] = None, storeId: Optional[Any] = None, merchantId: Optional[Any] = None, idOffset: Optional[Any] = None, dateTimeOffset: Optional[Any] = None, pageSize: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getGVList``
                Query: statusFilter, storeId, merchantId, idOffset, dateTimeOffset, pageSize
        """
        params: Dict[str, Any] = {}
        if statusFilter is not None: params['statusFilter'] = statusFilter
        if storeId is not None: params['storeId'] = storeId
        if merchantId is not None: params['merchantId'] = merchantId
        if idOffset is not None: params['idOffset'] = idOffset
        if dateTimeOffset is not None: params['dateTimeOffset'] = dateTimeOffset
        if pageSize is not None: params['pageSize'] = pageSize
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getGVList', params=params)

    def get_kyc_display_info(self, *, requestKycTypes: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getKycDisplayInfo``
                Query: requestKycTypes
        """
        params: Dict[str, Any] = {}
        if requestKycTypes is not None: params['requestKycTypes'] = requestKycTypes
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getKycDisplayInfo', params=params)

    def get_kyc_input_lists(self, *, inputLists: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getKycInputLists``
                Query: inputLists
        """
        params: Dict[str, Any] = {}
        if inputLists is not None: params['inputLists'] = inputLists
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getKycInputLists', params=params)

    def get_kyc_nri_auth_info(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getKycNriAuthInfo``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getKycNriAuthInfo', params=params or None)

    def get_localized_string(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/getLocalizedString``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/getLocalizedString', json=body)

    def get_login_devices(self, *, pageNumber: Optional[Any] = None, pageSize: Optional[Any] = None, authenticated: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getLoginDevices``
                Query: pageNumber, pageSize, authenticated
        """
        params: Dict[str, Any] = {}
        if pageNumber is not None: params['pageNumber'] = pageNumber
        if pageSize is not None: params['pageSize'] = pageSize
        if authenticated is not None: params['authenticated'] = authenticated
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getLoginDevices', params=params)

    def get_notification_center_display_info(self, *, selectedTabId: Optional[Any] = None, requestStartTs: Optional[Any] = None, nextPageToken: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getNotificationCenterDisplayInfo``
                Query: selectedTabId, requestStartTs, nextPageToken
        """
        params: Dict[str, Any] = {}
        if selectedTabId is not None: params['selectedTabId'] = selectedTabId
        if requestStartTs is not None: params['requestStartTs'] = requestStartTs
        if nextPageToken is not None: params['nextPageToken'] = nextPageToken
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getNotificationCenterDisplayInfo', params=params)

    def get_nri_auth_info(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getNriAuthInfo``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getNriAuthInfo', params=params or None)

    def get_order_by_order_id(self, *, orderId: Optional[Any] = None, orderType: Optional[Any] = None, refundId: Optional[Any] = None, showToastMessage: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getOrderByOrderId``
                Query: orderId, orderType, refundId, showToastMessage
        """
        params: Dict[str, Any] = {}
        if orderId is not None: params['orderId'] = orderId
        if orderType is not None: params['orderType'] = orderType
        if refundId is not None: params['refundId'] = refundId
        if showToastMessage is not None: params['showToastMessage'] = showToastMessage
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getOrderByOrderId', params=params)

    def get_p2p_message(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/getP2PMessage``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/getP2PMessage', json=body)

    def get_p2p_request_order(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/getP2PRequestOrder``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/getP2PRequestOrder', json=body)

    def get_p2p_theme_list(self, *, type: Optional[Any] = None, group: Optional[Any] = None, isSecretEnvelope: Optional[Any] = None, feedId: Optional[Any] = None, themeId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getP2PThemeList``
                Query: type, group, isSecretEnvelope, feedId, themeId
        """
        params: Dict[str, Any] = {}
        if type is not None: params['type'] = type
        if group is not None: params['group'] = group
        if isSecretEnvelope is not None: params['isSecretEnvelope'] = isSecretEnvelope
        if feedId is not None: params['feedId'] = feedId
        if themeId is not None: params['themeId'] = themeId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getP2PThemeList', params=params)

    def get_p2p_user_search_history(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getP2PUserSearchHistory``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getP2PUserSearchHistory', params=params or None)

    def get_pay2_balance_cancelled_pending_cash_back_history(self, *, pageSize: Optional[Any] = None, lastSequence: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getPay2BalanceCancelledPendingCashBackHistory``
                Query: pageSize, lastSequence
        """
        params: Dict[str, Any] = {}
        if pageSize is not None: params['pageSize'] = pageSize
        if lastSequence is not None: params['lastSequence'] = lastSequence
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getPay2BalanceCancelledPendingCashBackHistory', params=params)

    def get_payment_detail_display_info(self, *, orderId: Optional[Any] = None, orderType: Optional[Any] = None, orderStatus: Optional[Any] = None, externalUserId: Optional[Any] = None, displayName: Optional[Any] = None, avatarImageUrl: Optional[Any] = None, merchantName: Optional[Any] = None, dateTime: Optional[Any] = None, totalAmount: Optional[Any] = None, merchantId: Optional[Any] = None, storeId: Optional[Any] = None, isEBillAutoPaymentEnabled: Optional[Any] = None, pids: Optional[Any] = None, mode: Optional[Any] = None, route: Optional[Any] = None, gvReferenceId: Optional[Any] = None, usingPaymentInfoV2: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getPaymentDetailDisplayInfo``
                Query: orderId, orderType, orderStatus, externalUserId, displayName, avatarImageUrl, merchantName, dateTime, totalAmount, merchantId, storeId, isEBillAutoPaymentEnabled, pids, mode, route, gvReferenceId, usingPaymentInfoV2
        """
        params: Dict[str, Any] = {}
        if orderId is not None: params['orderId'] = orderId
        if orderType is not None: params['orderType'] = orderType
        if orderStatus is not None: params['orderStatus'] = orderStatus
        if externalUserId is not None: params['externalUserId'] = externalUserId
        if displayName is not None: params['displayName'] = displayName
        if avatarImageUrl is not None: params['avatarImageUrl'] = avatarImageUrl
        if merchantName is not None: params['merchantName'] = merchantName
        if dateTime is not None: params['dateTime'] = dateTime
        if totalAmount is not None: params['totalAmount'] = totalAmount
        if merchantId is not None: params['merchantId'] = merchantId
        if storeId is not None: params['storeId'] = storeId
        if isEBillAutoPaymentEnabled is not None: params['isEBillAutoPaymentEnabled'] = isEBillAutoPaymentEnabled
        if pids is not None: params['pids'] = pids
        if mode is not None: params['mode'] = mode
        if route is not None: params['route'] = route
        if gvReferenceId is not None: params['gvReferenceId'] = gvReferenceId
        if usingPaymentInfoV2 is not None: params['usingPaymentInfoV2'] = usingPaymentInfoV2
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getPaymentDetailDisplayInfo', params=params)

    def get_payment_history_filter_condition(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getPaymentHistoryFilterCondition``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getPaymentHistoryFilterCondition', params=params or None)

    def get_payment_preferences(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/getPaymentPreferences``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/getPaymentPreferences', json=body)

    def get_pending_continuous_payment_list(self, *, pageNumber: Optional[Any] = None, pageSize: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getPendingContinuousPaymentList``
                Query: pageNumber, pageSize
        """
        params: Dict[str, Any] = {}
        if pageNumber is not None: params['pageNumber'] = pageNumber
        if pageSize is not None: params['pageSize'] = pageSize
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getPendingContinuousPaymentList', params=params)

    def get_pre_auth_display_info(self, *, orderId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getPreAuthDisplayInfo``
                Query: orderId
        """
        params: Dict[str, Any] = {}
        if orderId is not None: params['orderId'] = orderId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getPreAuthDisplayInfo', params=params)

    def get_pre_transaction_auto_topup_configuration(self, *, includePaymentMethodList: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getPreTransactionAutoTopupConfiguration``
                Query: includePaymentMethodList
        """
        params: Dict[str, Any] = {}
        if includePaymentMethodList is not None: params['includePaymentMethodList'] = includePaymentMethodList
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getPreTransactionAutoTopupConfiguration', params=params)

    def get_re_auth_display_info(self, *, internalRequestId: Optional[Any] = None, redirectUrl: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getReAuthDisplayInfo``
                Query: internalRequestId, redirectUrl
        """
        params: Dict[str, Any] = {}
        if internalRequestId is not None: params['internalRequestId'] = internalRequestId
        if redirectUrl is not None: params['redirectUrl'] = redirectUrl
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getReAuthDisplayInfo', params=params)

    def get_service_status(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getServiceStatus``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getServiceStatus', params=params or None)

    def get_smart_login_session(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getSmartLoginSession``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getSmartLoginSession', params=params or None)

    def get_softbank_login_session(self, *, display: Optional[Any] = None, redirectUrl: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getSoftbankLoginSession``
                Query: display, redirectUrl
        """
        params: Dict[str, Any] = {}
        if display is not None: params['display'] = display
        if redirectUrl is not None: params['redirectUrl'] = redirectUrl
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getSoftbankLoginSession', params=params)

    def get_source_order(self, *, orderId: Optional[Any] = None, orderType: Optional[Any] = None, orderStatus: Optional[Any] = None, subOrderId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getSourceOrder``
                Query: orderId, orderType, orderStatus, subOrderId
        """
        params: Dict[str, Any] = {}
        if orderId is not None: params['orderId'] = orderId
        if orderType is not None: params['orderType'] = orderType
        if orderStatus is not None: params['orderStatus'] = orderStatus
        if subOrderId is not None: params['subOrderId'] = subOrderId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getSourceOrder', params=params)

    def get_tpoint_token(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getTpointToken``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getTpointToken', params=params or None)

    def get_user_profile(self, *, includeSkinInfo: Optional[Any] = None, includeUserScore: Optional[Any] = None, includeBeginnerFlag: Optional[Any] = None, includeExternalProfileSync: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getUserProfile``
                Query: includeSkinInfo, includeUserScore, includeBeginnerFlag, includeExternalProfileSync
        """
        params: Dict[str, Any] = {}
        if includeSkinInfo is not None: params['includeSkinInfo'] = includeSkinInfo
        if includeUserScore is not None: params['includeUserScore'] = includeUserScore
        if includeBeginnerFlag is not None: params['includeBeginnerFlag'] = includeBeginnerFlag
        if includeExternalProfileSync is not None: params['includeExternalProfileSync'] = includeExternalProfileSync
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getUserProfile', params=params)

    def get_wallet_widget_info(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/getWalletWidgetInfo``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/getWalletWidgetInfo', json=body)

    def get_yahoo_wallet_token(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getYahooWalletToken``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v1/getYahooWalletToken', params=params or None)

    def get_yconnect_login_session(self, *, promptLogin: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v1/getYconnectLoginSession``
                Query: promptLogin
        """
        params: Dict[str, Any] = {}
        if promptLogin is not None: params['promptLogin'] = promptLogin
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v1/getYconnectLoginSession', params=params)

    def issue_lesser_token_ott(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/issueLesserTokenOTT``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/issueLesserTokenOTT', json=body)

    def like_feed(self, *, feedId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/likeFeed``
                Body: feedId
        """
        body: Dict[str, Any] = {}
        if feedId is not None: body['feedId'] = feedId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/likeFeed', json=body)

    def link_softbank(self, *, sessionId: Optional[Any] = None, state: Optional[Any] = None, code: Optional[Any] = None, redirectUrl: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/linkSoftbank``
                Body: sessionId, state, code, redirectUrl
        """
        body: Dict[str, Any] = {}
        if sessionId is not None: body['sessionId'] = sessionId
        if state is not None: body['state'] = state
        if code is not None: body['code'] = code
        if redirectUrl is not None: body['redirectUrl'] = redirectUrl
        body.update(extra)
        return self._c._request("POST", 'bff/v1/linkSoftbank', json=body)

    def link_yconnect(self, *, sessionId: Optional[Any] = None, state: Optional[Any] = None, code: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/linkYconnect``
                Body: sessionId, state, code
        """
        body: Dict[str, Any] = {}
        if sessionId is not None: body['sessionId'] = sessionId
        if state is not None: body['state'] = state
        if code is not None: body['code'] = code
        body.update(extra)
        return self._c._request("POST", 'bff/v1/linkYconnect', json=body)

    def make_all_tabs_read(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/makeAllTabsRead``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/makeAllTabsRead', json=body)

    def register_credit_card(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/registerCreditCard``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/registerCreditCard', json=body)

    def register_kyc_info(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/registerKycInfo``
                Body is a typed ``KYCAddressDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/registerKycInfo', json=body)

    def register_paypay_id(self, *, payPayId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/registerPayPayId``
                Body: payPayId
        """
        body: Dict[str, Any] = {}
        if payPayId is not None: body['payPayId'] = payPayId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/registerPayPayId', json=body)

    def reject_p2p_request_money(self, *, channelUrl: Optional[Any] = None, messageId: Optional[Any] = None, requestId: Optional[Any] = None, requestMoneyId: Optional[Any] = None, type: Optional[Any] = None, themeId: Optional[Any] = None, socketConnection: Optional[Any] = None, externalUserId: Optional[Any] = None, phoneNumber: Optional[Any] = None, search: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/rejectP2PRequestMoney``
                Body: channelUrl, messageId, requestId, requestMoneyId, type, themeId, socketConnection
                Query: externalUserId, phoneNumber, search
        """
        body: Dict[str, Any] = {}
        if channelUrl is not None: body['channelUrl'] = channelUrl
        if messageId is not None: body['messageId'] = messageId
        if requestId is not None: body['requestId'] = requestId
        if requestMoneyId is not None: body['requestMoneyId'] = requestMoneyId
        if type is not None: body['type'] = type
        if themeId is not None: body['themeId'] = themeId
        if socketConnection is not None: body['socketConnection'] = socketConnection
        body.update(extra)
        params: Dict[str, Any] = {}
        if externalUserId is not None: params['externalUserId'] = externalUserId
        if phoneNumber is not None: params['phoneNumber'] = phoneNumber
        if search is not None: params['search'] = search
        return self._c._request("POST", 'bff/v1/rejectP2PRequestMoney', json=body, params=params or None)

    def reject_p2p_send_money(self, *, channelUrl: Optional[Any] = None, messageId: Optional[Any] = None, orderId: Optional[Any] = None, requestId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/rejectP2PSendMoney``
                Body: channelUrl, messageId, orderId, requestId
        """
        body: Dict[str, Any] = {}
        if channelUrl is not None: body['channelUrl'] = channelUrl
        if messageId is not None: body['messageId'] = messageId
        if orderId is not None: body['orderId'] = orderId
        if requestId is not None: body['requestId'] = requestId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/rejectP2PSendMoney', json=body)

    def remove_user_defined_limit(self, *, otpReferenceId: Optional[Any] = None, otp: Optional[Any] = None, mode: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/removeUserDefinedLimit``
                Body: otpReferenceId, otp, mode
        """
        body: Dict[str, Any] = {}
        if otpReferenceId is not None: body['otpReferenceId'] = otpReferenceId
        if otp is not None: body['otp'] = otp
        if mode is not None: body['mode'] = mode
        body.update(extra)
        return self._c._request("POST", 'bff/v1/removeUserDefinedLimit', json=body)

    def resend_sms(self, *, otpReferenceId: Optional[Any] = None, type: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/resendSms``
                Body: otpReferenceId, type
        """
        body: Dict[str, Any] = {}
        if otpReferenceId is not None: body['otpReferenceId'] = otpReferenceId
        if type is not None: body['type'] = type
        body.update(extra)
        return self._c._request("POST", 'bff/v1/resendSms', json=body)

    def save_bank_standing_instruction(self, *, requestId: Optional[Any] = None, payoutMethodId: Optional[Any] = None, accountOwnership: Optional[Any] = None, senderName: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/saveBankStandingInstruction``
                Body: requestId, payoutMethodId, accountOwnership, senderName
        """
        body: Dict[str, Any] = {}
        if requestId is not None: body['requestId'] = requestId
        if payoutMethodId is not None: body['payoutMethodId'] = payoutMethodId
        if accountOwnership is not None: body['accountOwnership'] = accountOwnership
        if senderName is not None: body['senderName'] = senderName
        body.update(extra)
        return self._c._request("POST", 'bff/v1/saveBankStandingInstruction', json=body)

    def send_authorize_mail(self, *, mailAddress: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendAuthorizeMail``
                Body: mailAddress
        """
        body: Dict[str, Any] = {}
        if mailAddress is not None: body['mailAddress'] = mailAddress
        body.update(extra)
        return self._c._request("POST", 'bff/v1/sendAuthorizeMail', json=body)

    def send_credit_card_registration_failure(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendCreditCardRegistrationFailure``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/sendCreditCardRegistrationFailure', json=body)

    def send_delete_account_sms(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendDeleteAccountSms``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/sendDeleteAccountSms', json=body)

    def send_forget_link(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendForgetLink``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/sendForgetLink', json=body)

    def send_forget_mail(self, *, mailAddress: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendForgetMail``
                Body: mailAddress
        """
        body: Dict[str, Any] = {}
        if mailAddress is not None: body['mailAddress'] = mailAddress
        body.update(extra)
        return self._c._request("POST", 'bff/v1/sendForgetMail', json=body)

    def send_forget_sms(self, *, phoneNumber: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendForgetSms``
                Body: phoneNumber
        """
        body: Dict[str, Any] = {}
        if phoneNumber is not None: body['phoneNumber'] = phoneNumber
        body.update(extra)
        return self._c._request("POST", 'bff/v1/sendForgetSms', json=body)

    def send_otp_for_user_defined_limits(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/sendOtpForUserDefinedLimits``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/sendOtpForUserDefinedLimits', json=body)

    def set_prioritized_payment_method(self, *, paymentMethodType: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/setPrioritizedPaymentMethod``
                Body: paymentMethodType
        """
        body: Dict[str, Any] = {}
        if paymentMethodType is not None: body['paymentMethodType'] = paymentMethodType
        body.update(extra)
        return self._c._request("POST", 'bff/v1/setPrioritizedPaymentMethod', json=body)

    def set_user_defined_limit(self, *, otpReferenceId: Optional[Any] = None, otp: Optional[Any] = None, mode: Optional[Any] = None, dailyLimit: Optional[Any] = None, monthlyLimit: Optional[Any] = None, isLimitTypeAlreadySet: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/setUserDefinedLimit``
                Body: otpReferenceId, otp, mode, dailyLimit, monthlyLimit, isLimitTypeAlreadySet
        """
        body: Dict[str, Any] = {}
        if otpReferenceId is not None: body['otpReferenceId'] = otpReferenceId
        if otp is not None: body['otp'] = otp
        if mode is not None: body['mode'] = mode
        if dailyLimit is not None: body['dailyLimit'] = dailyLimit
        if monthlyLimit is not None: body['monthlyLimit'] = monthlyLimit
        if isLimitTypeAlreadySet is not None: body['isLimitTypeAlreadySet'] = isLimitTypeAlreadySet
        body.update(extra)
        return self._c._request("POST", 'bff/v1/setUserDefinedLimit', json=body)

    def set_user_defined_limit_type(self, *, limitType: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/setUserDefinedLimitType``
                Body: limitType
        """
        body: Dict[str, Any] = {}
        if limitType is not None: body['limitType'] = limitType
        body.update(extra)
        return self._c._request("POST", 'bff/v1/setUserDefinedLimitType', json=body)

    def share_feed(self, *, type: Optional[Any] = None, group: Optional[Any] = None, isSecretEnvelope: Optional[Any] = None, feedId: Optional[Any] = None, themeId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/shareFeed``
                Body: type, group, isSecretEnvelope
                Query: feedId, themeId
        """
        body: Dict[str, Any] = {}
        if type is not None: body['type'] = type
        if group is not None: body['group'] = group
        if isSecretEnvelope is not None: body['isSecretEnvelope'] = isSecretEnvelope
        body.update(extra)
        params: Dict[str, Any] = {}
        if feedId is not None: params['feedId'] = feedId
        if themeId is not None: params['themeId'] = themeId
        return self._c._request("POST", 'bff/v1/shareFeed', json=body, params=params or None)

    def sign_out(self, *, channelId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/signOut``
                Body: channelId
        """
        body: Dict[str, Any] = {}
        if channelId is not None: body['channelId'] = channelId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/signOut', json=body)

    def sign_out_and_delete_all_devices(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/signOutAndDeleteAllDevices``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/signOutAndDeleteAllDevices', json=body)

    def sign_out_and_delete_device(self, *, deviceUUID: Optional[Any] = None, clientId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/signOutAndDeleteDevice``
                Body: deviceUUID, clientId
        """
        body: Dict[str, Any] = {}
        if deviceUUID is not None: body['deviceUUID'] = deviceUUID
        if clientId is not None: body['clientId'] = clientId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/signOutAndDeleteDevice', json=body)

    def sync_external_user_profile(self, *, externalProvider: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/syncExternalUserProfile``
                Body: externalProvider
        """
        body: Dict[str, Any] = {}
        if externalProvider is not None: body['externalProvider'] = externalProvider
        body.update(extra)
        return self._c._request("POST", 'bff/v1/syncExternalUserProfile', json=body)

    def unfollow_channel(self, *, channelId: Optional[Any] = None, type: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/unfollowChannel``
                Body: channelId, type
        """
        body: Dict[str, Any] = {}
        if channelId is not None: body['channelId'] = channelId
        if type is not None: body['type'] = type
        body.update(extra)
        return self._c._request("POST", 'bff/v1/unfollowChannel', json=body)

    def unlike_feed(self, *, feedId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/unlikeFeed``
                Body: feedId
        """
        body: Dict[str, Any] = {}
        if feedId is not None: body['feedId'] = feedId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/unlikeFeed', json=body)

    def unlink_softbank(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/unlinkSoftbank``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/unlinkSoftbank', json=body)

    def unlink_yconnect(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/unlinkYconnect``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/unlinkYconnect', json=body)

    def update_device_lock_status(self, *, lockType: Optional[Any] = None, appSettingStatus: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateDeviceLockStatus``
                Body: lockType, appSettingStatus
        """
        body: Dict[str, Any] = {}
        if lockType is not None: body['lockType'] = lockType
        if appSettingStatus is not None: body['appSettingStatus'] = appSettingStatus
        body.update(extra)
        return self._c._request("POST", 'bff/v1/updateDeviceLockStatus', json=body)

    def update_gv_auto_select_configuration(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateGvAutoSelectConfiguration``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/updateGvAutoSelectConfiguration', json=body)

    def update_notification_status(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateNotificationStatus``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/updateNotificationStatus', json=body)

    def update_notification_status_bms_store(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateNotificationStatusBmsStore``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/updateNotificationStatusBmsStore', json=body)

    def update_open_payment_client_status(self, *, userAuthorizationId: Optional[Any] = None, status: Optional[Any] = None, clientId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateOpenPaymentClientStatus``
                Body: userAuthorizationId, status, clientId
        """
        body: Dict[str, Any] = {}
        if userAuthorizationId is not None: body['userAuthorizationId'] = userAuthorizationId
        if status is not None: body['status'] = status
        if clientId is not None: body['clientId'] = clientId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/updateOpenPaymentClientStatus', json=body)

    def update_pre_transaction_auto_topup_configuration(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updatePreTransactionAutoTopupConfiguration``
                Body is a typed ``UpdatePreTransactionAutoTopupConfigurationParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/updatePreTransactionAutoTopupConfiguration', json=body)

    def update_prioritized_payment_methods_configuration(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updatePrioritizedPaymentMethodsConfiguration``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/updatePrioritizedPaymentMethodsConfiguration', json=body)

    def update_thread_mute_status(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateThreadMuteStatus``
                Body is a typed ``UpdateThreadMuteStatusParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v1/updateThreadMuteStatus', json=body)

    def update_transaction_merchant_note(self, *, orderId: Optional[Any] = None, existingMerchantNote: Optional[Any] = None, newMerchantNote: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/updateTransactionMerchantNote``
                Body: orderId, existingMerchantNote, newMerchantNote
        """
        body: Dict[str, Any] = {}
        if orderId is not None: body['orderId'] = orderId
        if existingMerchantNote is not None: body['existingMerchantNote'] = existingMerchantNote
        if newMerchantNote is not None: body['newMerchantNote'] = newMerchantNote
        body.update(extra)
        return self._c._request("POST", 'bff/v1/updateTransactionMerchantNote', json=body)

    def validate_paypay_id(self, *, payPayId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/validatePayPayId``
                Body: payPayId
        """
        body: Dict[str, Any] = {}
        if payPayId is not None: body['payPayId'] = payPayId
        body.update(extra)
        return self._c._request("POST", 'bff/v1/validatePayPayId', json=body)

    def verify_kyc_info(self, *, idDocType: Optional[Any] = None, sessionId: Optional[Any] = None, eKycInfo: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/verifyKycInfo``
                Body: idDocType, sessionId, eKycInfo
        """
        body: Dict[str, Any] = {}
        if idDocType is not None: body['idDocType'] = idDocType
        if sessionId is not None: body['sessionId'] = sessionId
        if eKycInfo is not None: body['eKycInfo'] = eKycInfo
        body.update(extra)
        return self._c._request("POST", 'bff/v1/verifyKycInfo', json=body)

    def yconnect_login(self, *, sessionId: Optional[Any] = None, state: Optional[Any] = None, code: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v1/yconnectLogin``
                Body: sessionId, state, code
        """
        body: Dict[str, Any] = {}
        if sessionId is not None: body['sessionId'] = sessionId
        if state is not None: body['state'] = state
        if code is not None: body['code'] = code
        body.update(extra)
        return self._c._request("POST", 'bff/v1/yconnectLogin', json=body)

    def accept_p2p_send_money_link(self, *, requestId: Optional[Any] = None, orderId: Optional[Any] = None, verificationCode: Optional[Any] = None, passcode: Optional[Any] = None, senderMessageId: Optional[Any] = None, senderChannelUrl: Optional[Any] = None, appContext: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/acceptP2PSendMoneyLink``
                Body: requestId, orderId, verificationCode, passcode, senderMessageId, senderChannelUrl
                Query: appContext
        """
        body: Dict[str, Any] = {}
        if requestId is not None: body['requestId'] = requestId
        if orderId is not None: body['orderId'] = orderId
        if verificationCode is not None: body['verificationCode'] = verificationCode
        if passcode is not None: body['passcode'] = passcode
        if senderMessageId is not None: body['senderMessageId'] = senderMessageId
        if senderChannelUrl is not None: body['senderChannelUrl'] = senderChannelUrl
        body.update(extra)
        params: Dict[str, Any] = {}
        if appContext is not None: params['appContext'] = appContext
        return self._c._request("POST", 'bff/v2/acceptP2PSendMoneyLink', json=body, params=params or None)

    def bind_push_notification_device(self, *, channelId: Optional[Any] = None, fcmToken: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/bindPushNotificationDevice``
                Body: channelId, fcmToken
        """
        body: Dict[str, Any] = {}
        if channelId is not None: body['channelId'] = channelId
        if fcmToken is not None: body['fcmToken'] = fcmToken
        body.update(extra)
        return self._c._request("POST", 'bff/v2/bindPushNotificationDevice', json=body)

    def check_threed_secure_status(self, *, paymentMethodId: Optional[Any] = None, type: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/check3dSecureStatus``
                Body: paymentMethodId, type
        """
        body: Dict[str, Any] = {}
        if paymentMethodId is not None: body['paymentMethodId'] = paymentMethodId
        if type is not None: body['type'] = type
        body.update(extra)
        return self._c._request("POST", 'bff/v2/check3dSecureStatus', json=body)

    def execute_p2p_request_money(self, *, theme: Optional[Any] = None, userComment: Optional[Any] = None, requestId: Optional[Any] = None, externalSenderId: Optional[Any] = None, source: Optional[Any] = None, cmsImageId: Optional[Any] = None, userCommentCreatorType: Optional[Any] = None, unblockReceiver: Optional[Any] = None, socketConnection: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/executeP2PRequestMoney``
                Body: theme, userComment, requestId, externalSenderId, source, cmsImageId, userCommentCreatorType, unblockReceiver, socketConnection
        """
        body: Dict[str, Any] = {}
        if theme is not None: body['theme'] = theme
        if userComment is not None: body['userComment'] = userComment
        if requestId is not None: body['requestId'] = requestId
        if externalSenderId is not None: body['externalSenderId'] = externalSenderId
        if source is not None: body['source'] = source
        if cmsImageId is not None: body['cmsImageId'] = cmsImageId
        if userCommentCreatorType is not None: body['userCommentCreatorType'] = userCommentCreatorType
        if unblockReceiver is not None: body['unblockReceiver'] = unblockReceiver
        if socketConnection is not None: body['socketConnection'] = socketConnection
        body.update(extra)
        return self._c._request("POST", 'bff/v2/executeP2PRequestMoney', json=body)

    def execute_p2p_send_money_link(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/executeP2PSendMoneyLink``
                Body is a typed ``UserDefinedLimitInfoDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v2/executeP2PSendMoneyLink', json=body)

    def execute_pre_auth_payment(self, *, requestId: Optional[Any] = None, requestAt: Optional[Any] = None, orderId: Optional[Any] = None, merchantId: Optional[Any] = None, currency: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/executePreAuthPayment``
                Body: requestId, requestAt, orderId, merchantId, currency
        """
        body: Dict[str, Any] = {}
        if requestId is not None: body['requestId'] = requestId
        if requestAt is not None: body['requestAt'] = requestAt
        if orderId is not None: body['orderId'] = orderId
        if merchantId is not None: body['merchantId'] = merchantId
        if currency is not None: body['currency'] = currency
        body.update(extra)
        return self._c._request("POST", 'bff/v2/executePreAuthPayment', json=body)

    def execute_re_auth_payment(self, *, internalRequestId: Optional[Any] = None, currency: Optional[Any] = None, merchantId: Optional[Any] = None, orderId: Optional[Any] = None, redirectUrl: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/executeReAuthPayment``
                Body: internalRequestId, currency, merchantId, orderId, redirectUrl
        """
        body: Dict[str, Any] = {}
        if internalRequestId is not None: body['internalRequestId'] = internalRequestId
        if currency is not None: body['currency'] = currency
        if merchantId is not None: body['merchantId'] = merchantId
        if orderId is not None: body['orderId'] = orderId
        if redirectUrl is not None: body['redirectUrl'] = redirectUrl
        body.update(extra)
        return self._c._request("POST", 'bff/v2/executeReAuthPayment', json=body)

    def get_auto_topup_configuration(self, *, includePaymentMethodList: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getAutoTopupConfiguration``
                Query: includePaymentMethodList
        """
        params: Dict[str, Any] = {}
        if includePaymentMethodList is not None: params['includePaymentMethodList'] = includePaymentMethodList
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getAutoTopupConfiguration', params=params)

    def get_barcode_info(self, *, code: Optional[Any] = None, paymentMethodId: Optional[Any] = None, paymentMethodType: Optional[Any] = None, secondaryPaymentMethodId: Optional[Any] = None, secondaryPaymentMethodType: Optional[Any] = None, usePayPayPoints: Optional[Any] = None, lastSelectedHomePaymentMethodId: Optional[Any] = None, lastSelectedHomePaymentMethodType: Optional[Any] = None, lineTicket: Optional[Any] = None, pointPaymentAmount: Optional[Any] = None, isScannedFromFile: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getBarcodeInfo``
                Query: code, paymentMethodId, paymentMethodType, secondaryPaymentMethodId, secondaryPaymentMethodType, usePayPayPoints, lastSelectedHomePaymentMethodId, lastSelectedHomePaymentMethodType, lineTicket, pointPaymentAmount, isScannedFromFile
        """
        params: Dict[str, Any] = {}
        if code is not None: params['code'] = code
        if paymentMethodId is not None: params['paymentMethodId'] = paymentMethodId
        if paymentMethodType is not None: params['paymentMethodType'] = paymentMethodType
        if secondaryPaymentMethodId is not None: params['secondaryPaymentMethodId'] = secondaryPaymentMethodId
        if secondaryPaymentMethodType is not None: params['secondaryPaymentMethodType'] = secondaryPaymentMethodType
        if usePayPayPoints is not None: params['usePayPayPoints'] = usePayPayPoints
        if lastSelectedHomePaymentMethodId is not None: params['lastSelectedHomePaymentMethodId'] = lastSelectedHomePaymentMethodId
        if lastSelectedHomePaymentMethodType is not None: params['lastSelectedHomePaymentMethodType'] = lastSelectedHomePaymentMethodType
        if lineTicket is not None: params['lineTicket'] = lineTicket
        if pointPaymentAmount is not None: params['pointPaymentAmount'] = pointPaymentAmount
        if isScannedFromFile is not None: params['isScannedFromFile'] = isScannedFromFile
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getBarcodeInfo', params=params)

    def get_p2p_link_info(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/getP2PLinkInfo``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v2/getP2PLinkInfo', json=body)

    def get_pay2_balance_history(self, *, lastSequence: Optional[Any] = None, pageSize: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPay2BalanceHistory``
                Query: lastSequence, pageSize
        """
        params: Dict[str, Any] = {}
        if lastSequence is not None: params['lastSequence'] = lastSequence
        if pageSize is not None: params['pageSize'] = pageSize
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getPay2BalanceHistory', params=params)

    def get_payment_completion(self, *, paymentCodeSessionId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPaymentCompletion``
                Query: paymentCodeSessionId
        """
        params: Dict[str, Any] = {}
        if paymentCodeSessionId is not None: params['paymentCodeSessionId'] = paymentCodeSessionId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getPaymentCompletion', params=params)

    def get_payment_method_list(self, *, type: Optional[Any] = None, transactionType: Optional[Any] = None, merchantId: Optional[Any] = None, productType: Optional[Any] = None, usePayPayPoints: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPaymentMethodList``
                Query: type, transactionType, merchantId, productType, usePayPayPoints
        """
        params: Dict[str, Any] = {}
        if type is not None: params['type'] = type
        if transactionType is not None: params['transactionType'] = transactionType
        if merchantId is not None: params['merchantId'] = merchantId
        if productType is not None: params['productType'] = productType
        if usePayPayPoints is not None: params['usePayPayPoints'] = usePayPayPoints
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getPaymentMethodList', params=params)

    def get_payment_preferences_v2(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPaymentPreferences``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v2/getPaymentPreferences', params=params or None)

    def get_payout_display_info(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPayoutDisplayInfo``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v2/getPayoutDisplayInfo', params=params or None)

    def get_payout_info(self, *, payoutMethodId: Optional[Any] = None, mode: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPayoutInfo``
                Query: payoutMethodId, mode
        """
        params: Dict[str, Any] = {}
        if payoutMethodId is not None: params['payoutMethodId'] = payoutMethodId
        if mode is not None: params['mode'] = mode
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getPayoutInfo', params=params)

    def get_prioritized_payment_methods_configuration(self, *, onlyPreferredPaymentMethod: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getPrioritizedPaymentMethodsConfiguration``
                Query: onlyPreferredPaymentMethod
        """
        params: Dict[str, Any] = {}
        if onlyPreferredPaymentMethod is not None: params['onlyPreferredPaymentMethod'] = onlyPreferredPaymentMethod
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getPrioritizedPaymentMethodsConfiguration', params=params)

    def get_profile_display_info(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/getProfileDisplayInfo``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v2/getProfileDisplayInfo', json=body)

    def get_topup_display_info(self, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getTopupDisplayInfo``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'bff/v2/getTopupDisplayInfo', params=params or None)

    def get_wallet_display_info(self, *, giftVoucherExpiryWithinDays: Optional[Any] = None, pfmWidgetVariant: Optional[Any] = None, usingPaymentInfoV2: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v2/getWalletDisplayInfo``
                Query: giftVoucherExpiryWithinDays, pfmWidgetVariant, usingPaymentInfoV2
        """
        params: Dict[str, Any] = {}
        if giftVoucherExpiryWithinDays is not None: params['giftVoucherExpiryWithinDays'] = giftVoucherExpiryWithinDays
        if pfmWidgetVariant is not None: params['pfmWidgetVariant'] = pfmWidgetVariant
        if usingPaymentInfoV2 is not None: params['usingPaymentInfoV2'] = usingPaymentInfoV2
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v2/getWalletDisplayInfo', params=params)

    def oauth2_par(self, *, clientId: Optional[Any] = None, clientAppVersion: Optional[Any] = None, clientOsVersion: Optional[Any] = None, clientOsType: Optional[Any] = None, redirectUri: Optional[Any] = None, responseType: Optional[Any] = None, state: Optional[Any] = None, codeChallenge: Optional[Any] = None, codeChallengeMethod: Optional[Any] = None, scope: Optional[Any] = None, tokenVersion: Optional[Any] = None, prompt: Optional[Any] = None, uiLocales: Optional[Any] = None, referralCampaignCode: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/oauth2/par``
                Body: clientId, clientAppVersion, clientOsVersion, clientOsType, redirectUri, responseType, state, codeChallenge, codeChallengeMethod, scope, tokenVersion, prompt, uiLocales, referralCampaignCode
        """
        body: Dict[str, Any] = {}
        if clientId is not None: body['clientId'] = clientId
        if clientAppVersion is not None: body['clientAppVersion'] = clientAppVersion
        if clientOsVersion is not None: body['clientOsVersion'] = clientOsVersion
        if clientOsType is not None: body['clientOsType'] = clientOsType
        if redirectUri is not None: body['redirectUri'] = redirectUri
        if responseType is not None: body['responseType'] = responseType
        if state is not None: body['state'] = state
        if codeChallenge is not None: body['codeChallenge'] = codeChallenge
        if codeChallengeMethod is not None: body['codeChallengeMethod'] = codeChallengeMethod
        if scope is not None: body['scope'] = scope
        if tokenVersion is not None: body['tokenVersion'] = tokenVersion
        if prompt is not None: body['prompt'] = prompt
        if uiLocales is not None: body['uiLocales'] = uiLocales
        if referralCampaignCode is not None: body['referralCampaignCode'] = referralCampaignCode
        body.update(extra)
        return self._c._request("POST", 'bff/v2/oauth2/par', json=body)

    def oauth2_refresh(self, *, clientId: Optional[Any] = None, refreshToken: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/oauth2/refresh``
                Body: clientId, refreshToken
        """
        body: Dict[str, Any] = {}
        if clientId is not None: body['clientId'] = clientId
        if refreshToken is not None: body['refreshToken'] = refreshToken
        body.update(extra)
        return self._c._request("POST", 'bff/v2/oauth2/refresh', json=body)

    def oauth2_token(self, *, clientId: Optional[Any] = None, redirectUri: Optional[Any] = None, code: Optional[Any] = None, codeVerifier: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/oauth2/token``
                Body: clientId, redirectUri, code, codeVerifier
        """
        body: Dict[str, Any] = {}
        if clientId is not None: body['clientId'] = clientId
        if redirectUri is not None: body['redirectUri'] = redirectUri
        if code is not None: body['code'] = code
        if codeVerifier is not None: body['codeVerifier'] = codeVerifier
        body.update(extra)
        return self._c._request("POST", 'bff/v2/oauth2/token', json=body)

    def oauth2_token_exchange(self, *, refreshToken: Optional[Any] = None, destinationClientId: Optional[Any] = None, codeChallenge: Optional[Any] = None, codeVerifier: Optional[Any] = None, state: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/oauth2/token/exchange``
                Body: refreshToken, destinationClientId, codeChallenge, codeVerifier, state
        """
        body: Dict[str, Any] = {}
        if refreshToken is not None: body['refreshToken'] = refreshToken
        if destinationClientId is not None: body['destinationClientId'] = destinationClientId
        if codeChallenge is not None: body['codeChallenge'] = codeChallenge
        if codeVerifier is not None: body['codeVerifier'] = codeVerifier
        if state is not None: body['state'] = state
        body.update(extra)
        return self._c._request("POST", 'bff/v2/oauth2/token/exchange', json=body)

    def reject_p2p_send_money_link(self, *, requestId: Optional[Any] = None, orderId: Optional[Any] = None, verificationCode: Optional[Any] = None, senderMessageId: Optional[Any] = None, senderChannelUrl: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/rejectP2PSendMoneyLink``
                Body: requestId, orderId, verificationCode, senderMessageId, senderChannelUrl
        """
        body: Dict[str, Any] = {}
        if requestId is not None: body['requestId'] = requestId
        if orderId is not None: body['orderId'] = orderId
        if verificationCode is not None: body['verificationCode'] = verificationCode
        if senderMessageId is not None: body['senderMessageId'] = senderMessageId
        if senderChannelUrl is not None: body['senderChannelUrl'] = senderChannelUrl
        body.update(extra)
        return self._c._request("POST", 'bff/v2/rejectP2PSendMoneyLink', json=body)

    def update_auto_topup_configuration(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v2/updateAutoTopupConfiguration``
                Body is a typed ``UpdateAutoTopupConfigurationParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v2/updateAutoTopupConfiguration', json=body)

    def create_payment_one_time_code(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v3/createPaymentOneTimeCode``
                Body is a typed ``CreatePaymentOneTimeCodeParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v3/createPaymentOneTimeCode', json=body)

    def create_payment_one_time_code_for_home(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v3/createPaymentOneTimeCodeForHome``
                Body is a typed ``CreatePaymentOneTimeCodeForHomeParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v3/createPaymentOneTimeCodeForHome', json=body)

    def get_order_by_order_id(self, *, orderId: Optional[Any] = None, orderType: Optional[Any] = None, refundId: Optional[Any] = None, showToastMessage: Optional[Any] = None, productType: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v3/getOrderByOrderId``
                Query: orderId, orderType, refundId, showToastMessage, productType
        """
        params: Dict[str, Any] = {}
        if orderId is not None: params['orderId'] = orderId
        if orderType is not None: params['orderType'] = orderType
        if refundId is not None: params['refundId'] = refundId
        if showToastMessage is not None: params['showToastMessage'] = showToastMessage
        if productType is not None: params['productType'] = productType
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v3/getOrderByOrderId', params=params)

    def get_cash_back_result(self, *, orderId: Optional[Any] = None, orderType: Optional[Any] = None, route: Optional[Any] = None, mode: Optional[Any] = None, merchantType: Optional[Any] = None, paymentMethodTypes: Optional[Any] = None, isPayPayCard: Optional[Any] = None, isCreditUser: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET bff/v4/getCashBackResult``
                Query: orderId, orderType, route, mode, merchantType, paymentMethodTypes, isPayPayCard, isCreditUser
        """
        params: Dict[str, Any] = {}
        if orderId is not None: params['orderId'] = orderId
        if orderType is not None: params['orderType'] = orderType
        if route is not None: params['route'] = route
        if mode is not None: params['mode'] = mode
        if merchantType is not None: params['merchantType'] = merchantType
        if paymentMethodTypes is not None: params['paymentMethodTypes'] = paymentMethodTypes
        if isPayPayCard is not None: params['isPayPayCard'] = isPayPayCard
        if isCreditUser is not None: params['isCreditUser'] = isCreditUser
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'bff/v4/getCashBackResult', params=params)

    def get_payment_history(self, **extra: Any) -> Dict[str, Any]:
        """``POST bff/v4/getPaymentHistory``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'bff/v4/getPaymentHistory', json=body)

    def genai_chatroom_get_chatroom(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/chatroom/getChatroom``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/chatroom/getChatroom', json=body)

    def genai_chatroom_get_history_messages(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/chatroom/getHistoryMessages``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/chatroom/getHistoryMessages', json=body)

    def genai_consent_user(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/consent/user``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/consent/user', json=body)

    def genai_feedback(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/feedback``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/feedback', json=body)

    def genai_p2p_get_image(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/p2p/getImage``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/p2p/getImage', json=body)

    def genai_p2p_get_images(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/p2p/getImages``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/p2p/getImages', json=body)

    def genai_p2p_health(self, **extra: Any) -> Dict[str, Any]:
        """``GET genai-bff/api/v1/p2p/health``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'genai-bff/api/v1/p2p/health', params=params or None)

    def genai_sse_get_stream_id(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/sse/getStreamId``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/sse/getStreamId', json=body)

    def genai_sse_p2p_get_stream_id(self, **extra: Any) -> Dict[str, Any]:
        """``POST genai-bff/api/v1/sse/p2p/getStreamId``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'genai-bff/api/v1/sse/p2p/getStreamId', json=body)

    def kyc_app_nri_auth(self, **extra: Any) -> Dict[str, Any]:
        """``GET kyc/v1/app/nri/auth``
                Body is a typed ``NRIAuthInfoResponseDTO`` in the app; pass fields via **extra.
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'kyc/v1/app/nri/auth', params=params or None)

    def add_p2p_friend(self, *, appContext: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/addP2PFriend``
                Body: appContext
        """
        body: Dict[str, Any] = {}
        if appContext is not None: body['appContext'] = appContext
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/addP2PFriend', json=body)

    def assign_group_chat_admin(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/assignGroupChatAdmin``
                Body is a typed ``P2PAssignGroupChatAdminParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/assignGroupChatAdmin', json=body)

    def block_user(self, *, externalId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/blockUser``
                Body: externalId
        """
        body: Dict[str, Any] = {}
        if externalId is not None: body['externalId'] = externalId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/blockUser', json=body)

    def cancel_group_pay(self, *, splitBillId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/cancelGroupPay``
                Body: splitBillId
        """
        body: Dict[str, Any] = {}
        if splitBillId is not None: body['splitBillId'] = splitBillId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/cancelGroupPay', json=body)

    def cancel_recurring_transfer(self, *, receiverExternalId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/cancelRecurringTransfer``
                Body: receiverExternalId
        """
        body: Dict[str, Any] = {}
        if receiverExternalId is not None: body['receiverExternalId'] = receiverExternalId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/cancelRecurringTransfer', json=body)

    def change_p2p_phone_book_discoverability(self, *, phonebookDiscoverabilityFlag: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/changeP2PPhoneBookDiscoverability``
                Body: phonebookDiscoverabilityFlag
        """
        body: Dict[str, Any] = {}
        if phonebookDiscoverabilityFlag is not None: body['phonebookDiscoverabilityFlag'] = phonebookDiscoverabilityFlag
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/changeP2PPhoneBookDiscoverability', json=body)

    def create_chat_invite_link(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createChatInviteLink``
                Body is a typed ``CreateChatInviteLinkParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/createChatInviteLink', json=body)

    def create_group_invite_link(self, *, chatRoomId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createGroupInviteLink``
                Body: chatRoomId
        """
        body: Dict[str, Any] = {}
        if chatRoomId is not None: body['chatRoomId'] = chatRoomId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/createGroupInviteLink', json=body)

    def create_group_pay(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createGroupPay``
                Body is a typed ``P2PGroupPayParticipantDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/createGroupPay', json=body)

    def create_p2p_group_channel(self, *, appContext: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createP2PGroupChannel``
                Body: appContext
        """
        body: Dict[str, Any] = {}
        if appContext is not None: body['appContext'] = appContext
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/createP2PGroupChannel', json=body)

    def create_p2p_group_invite_code(self, *, chatRoomId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createP2PGroupInviteCode``
                Body: chatRoomId
        """
        body: Dict[str, Any] = {}
        if chatRoomId is not None: body['chatRoomId'] = chatRoomId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/createP2PGroupInviteCode', json=body)

    def create_recurring_transfer(self, *, requestId: Optional[Any] = None, receiverExternalId: Optional[Any] = None, userComment: Optional[Any] = None, startDate: Optional[Any] = None, endDate: Optional[Any] = None, scheduleType: Optional[Any] = None, unblockReceiver: Optional[Any] = None, socketConnection: Optional[Any] = None, themeId: Optional[Any] = None, ackPhoneCallDetected: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createRecurringTransfer``
                Body: requestId, receiverExternalId, userComment, startDate, endDate, scheduleType, unblockReceiver, socketConnection, themeId, ackPhoneCallDetected
        """
        body: Dict[str, Any] = {}
        if requestId is not None: body['requestId'] = requestId
        if receiverExternalId is not None: body['receiverExternalId'] = receiverExternalId
        if userComment is not None: body['userComment'] = userComment
        if startDate is not None: body['startDate'] = startDate
        if endDate is not None: body['endDate'] = endDate
        if scheduleType is not None: body['scheduleType'] = scheduleType
        if unblockReceiver is not None: body['unblockReceiver'] = unblockReceiver
        if socketConnection is not None: body['socketConnection'] = socketConnection
        if themeId is not None: body['themeId'] = themeId
        if ackPhoneCallDetected is not None: body['ackPhoneCallDetected'] = ackPhoneCallDetected
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/createRecurringTransfer', json=body)

    def create_standing_order(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/createStandingOrder``
                Body is a typed ``CreateStandingOrderParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/createStandingOrder', json=body)

    def decline_group_pay(self, *, splitBillId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/declineGroupPay``
                Body: splitBillId
        """
        body: Dict[str, Any] = {}
        if splitBillId is not None: body['splitBillId'] = splitBillId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/declineGroupPay', json=body)

    def get_chat_room_has_message_from_user(self, *, chatRoomId: Optional[Any] = None, externalUserId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getChatRoomHasMessageFromUser``
                Query: chatRoomId, externalUserId
        """
        params: Dict[str, Any] = {}
        if chatRoomId is not None: params['chatRoomId'] = chatRoomId
        if externalUserId is not None: params['externalUserId'] = externalUserId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getChatRoomHasMessageFromUser', params=params)

    def get_group_chat_members(self, *, pageSize: Optional[Any] = None, showSmartFunction: Optional[Any] = None, channelId: Optional[Any] = None, lastSequence: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getGroupChatMembers``
                Query: pageSize, showSmartFunction, channelId, lastSequence
        """
        params: Dict[str, Any] = {}
        if pageSize is not None: params['pageSize'] = pageSize
        if showSmartFunction is not None: params['showSmartFunction'] = showSmartFunction
        if channelId is not None: params['channelId'] = channelId
        if lastSequence is not None: params['lastSequence'] = lastSequence
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getGroupChatMembers', params=params)

    def get_group_pay(self, *, splitBillId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getGroupPay``
                Query: splitBillId
        """
        params: Dict[str, Any] = {}
        if splitBillId is not None: params['splitBillId'] = splitBillId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getGroupPay', params=params)

    def get_group_pay_banner(self, *, channelId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getGroupPayBanner``
                Query: channelId
        """
        params: Dict[str, Any] = {}
        if channelId is not None: params['channelId'] = channelId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getGroupPayBanner', params=params)

    def get_group_pay_list(self, *, page: Optional[Any] = None, size: Optional[Any] = None, channelId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getGroupPayList``
                Query: page, size, channelId
        """
        params: Dict[str, Any] = {}
        if page is not None: params['page'] = page
        if size is not None: params['size'] = size
        if channelId is not None: params['channelId'] = channelId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getGroupPayList', params=params)

    def get_group_pay_potential_participants(self, *, channelId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getGroupPayPotentialParticipants``
                Query: channelId
        """
        params: Dict[str, Any] = {}
        if channelId is not None: params['channelId'] = channelId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getGroupPayPotentialParticipants', params=params)

    def get_p2p_friends(self, *, pageSize: Optional[Any] = None, pageToken: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getP2PFriends``
                Query: pageSize, pageToken
        """
        params: Dict[str, Any] = {}
        if pageSize is not None: params['pageSize'] = pageSize
        if pageToken is not None: params['pageToken'] = pageToken
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getP2PFriends', params=params)

    def get_p2p_group_chat_room(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/getP2PGroupChatRoom``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/getP2PGroupChatRoom', json=body)

    def get_p2p_home_content(self, *, variation: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getP2PHomeContent``
                Query: variation
        """
        params: Dict[str, Any] = {}
        if variation is not None: params['variation'] = variation
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getP2PHomeContent', params=params)

    def get_p2p_phone_book_discoverability(self, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getP2PPhoneBookDiscoverability``
        """
        params = {k: v for k, v in extra.items() if v is not None}
        return self._c._request("GET", 'p2p/v1/getP2PPhoneBookDiscoverability', params=params or None)

    def get_recurring_transfer_info(self, *, receiverExternalId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getRecurringTransferInfo``
                Query: receiverExternalId
        """
        params: Dict[str, Any] = {}
        if receiverExternalId is not None: params['receiverExternalId'] = receiverExternalId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getRecurringTransferInfo', params=params)

    def get_user_info_from_barcode(self, *, code: Optional[Any] = None, appContext: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/getUserInfoFromBarcode``
                Query: code, appContext
        """
        params: Dict[str, Any] = {}
        if code is not None: params['code'] = code
        if appContext is not None: params['appContext'] = appContext
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/getUserInfoFromBarcode', params=params)

    def initialise_one_to_one_and_link_chat_room(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/initialiseOneToOneAndLinkChatRoom``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/initialiseOneToOneAndLinkChatRoom', json=body)

    def invite_p2p_group_channel(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/inviteP2PGroupChannel``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/inviteP2PGroupChannel', json=body)

    def is_p2p_user_friend(self, *, externalUserId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/isP2PUserFriend``
                Query: externalUserId
        """
        params: Dict[str, Any] = {}
        if externalUserId is not None: params['externalUserId'] = externalUserId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/isP2PUserFriend', params=params)

    def leave_p2p_group_channel(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/leaveP2PGroupChannel``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/leaveP2PGroupChannel', json=body)

    def pay_group_pay(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/payGroupPay``
                Body is a typed ``UserDefinedLimitInfoDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/payGroupPay', json=body)

    def remove_group_chat_member(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/removeGroupChatMember``
                Body is a typed ``P2PRemoveGroupChatAdminParameterDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/removeGroupChatMember', json=body)

    def resend_recurring_transfer(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/resendRecurringTransfer``
                Body is a typed ``UserDefinedLimitInfoDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/resendRecurringTransfer', json=body)

    def resolve_link(self, *, type: Optional[Any] = None, code: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v1/resolveLink``
                Query: type, code
        """
        params: Dict[str, Any] = {}
        if type is not None: params['type'] = type
        if code is not None: params['code'] = code
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v1/resolveLink', params=params)

    def send_p2p_message(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/sendP2PMessage``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/sendP2PMessage', json=body)

    def un_friend_p2p_user(self, *, externalUserId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/unFriendP2PUser``
                Body: externalUserId
        """
        body: Dict[str, Any] = {}
        if externalUserId is not None: body['externalUserId'] = externalUserId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/unFriendP2PUser', json=body)

    def unblock_user(self, *, externalId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/unblockUser``
                Body: externalId
        """
        body: Dict[str, Any] = {}
        if externalId is not None: body['externalId'] = externalId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/unblockUser', json=body)

    def unhide_channel(self, *, chatRoomId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/unhideChannel``
                Body: chatRoomId
        """
        body: Dict[str, Any] = {}
        if chatRoomId is not None: body['chatRoomId'] = chatRoomId
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/unhideChannel', json=body)

    def update_p2p_friend_custom_name(self, *, friendExternalUserId: Optional[Any] = None, customDisplayName: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/updateP2PFriendCustomName``
                Body: friendExternalUserId, customDisplayName
        """
        body: Dict[str, Any] = {}
        if friendExternalUserId is not None: body['friendExternalUserId'] = friendExternalUserId
        if customDisplayName is not None: body['customDisplayName'] = customDisplayName
        body.update(extra)
        return self._c._request("POST", 'p2p/v1/updateP2PFriendCustomName', json=body)

    def update_p2p_group_channel(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/updateP2PGroupChannel``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/updateP2PGroupChannel', json=body)

    def upload_p2p_group_icon(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v1/uploadP2PGroupIcon``
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v1/uploadP2PGroupIcon', json=body)

    def get_p2p_info(self, *, channelUrl: Optional[Any] = None, messageId: Optional[Any] = None, requestId: Optional[Any] = None, requestMoneyId: Optional[Any] = None, type: Optional[Any] = None, themeId: Optional[Any] = None, socketConnection: Optional[Any] = None, externalUserId: Optional[Any] = None, phoneNumber: Optional[Any] = None, search: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v2/getP2PInfo``
                Query: channelUrl, messageId, requestId, requestMoneyId, type, themeId, socketConnection, externalUserId, phoneNumber, search
        """
        params: Dict[str, Any] = {}
        if channelUrl is not None: params['channelUrl'] = channelUrl
        if messageId is not None: params['messageId'] = messageId
        if requestId is not None: params['requestId'] = requestId
        if requestMoneyId is not None: params['requestMoneyId'] = requestMoneyId
        if type is not None: params['type'] = type
        if themeId is not None: params['themeId'] = themeId
        if socketConnection is not None: params['socketConnection'] = socketConnection
        if externalUserId is not None: params['externalUserId'] = externalUserId
        if phoneNumber is not None: params['phoneNumber'] = phoneNumber
        if search is not None: params['search'] = search
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v2/getP2PInfo', params=params)

    def get_preset_amount(self, *, receiverExternalUserId: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``GET p2p/v2/getPresetAmount``
                Query: receiverExternalUserId
        """
        params: Dict[str, Any] = {}
        if receiverExternalUserId is not None: params['receiverExternalUserId'] = receiverExternalUserId
        params.update({k: v for k, v in extra.items() if v is not None})
        return self._c._request("GET", 'p2p/v2/getPresetAmount', params=params)

    def execute_p2p_send_money(self, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v3/executeP2PSendMoney``
                Body is a typed ``UserDefinedLimitInfoDTO`` in the app; pass fields via **extra.
        """
        body: Dict[str, Any] = dict(extra)
        return self._c._request("POST", 'p2p/v3/executeP2PSendMoney', json=body)

    def search_p2p_user(self, *, searchTerm: Optional[Any] = None, pageToken: Optional[Any] = None, pageSize: Optional[Any] = None, isIngressSendMoney: Optional[Any] = None, searchTypes: Optional[Any] = None, **extra: Any) -> Dict[str, Any]:
        """``POST p2p/v3/searchP2PUser``
                Body: searchTerm, pageToken, pageSize, isIngressSendMoney, searchTypes
        """
        body: Dict[str, Any] = {}
        if searchTerm is not None: body['searchTerm'] = searchTerm
        if pageToken is not None: body['pageToken'] = pageToken
        if pageSize is not None: body['pageSize'] = pageSize
        if isIngressSendMoney is not None: body['isIngressSendMoney'] = isIngressSendMoney
        if searchTypes is not None: body['searchTypes'] = searchTypes
        body.update(extra)
        return self._c._request("POST", 'p2p/v3/searchP2PUser', json=body)


__all__ = ['RawAPI']