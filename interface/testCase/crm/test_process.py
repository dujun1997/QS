# -*- coding: utf-8 -*-
# @Time    : 2021/7/6 13:53
# @Author  : dujun
# @File    : test_process.py
# @describe: CRM订单分配流程

import time
import allure
import pytest
from interface.data.order_data import order_data
from interface.testCaseManage.crm.general import crm_general
from interface.testCaseManage.xdd2_manage.assert_xdd2 import xdd2_assert


@pytest.mark.usefixtures('setup_process')
@allure.feature('关闭手工截单按钮和手工截单按钮')
class Test_allButton_close:

    @allure.story('不符合展位--不符合非定制非电核广告--进入好单客源')
    def test_case1(self, appAddOrder):
        """
        同时关闭人工和手工截单按钮
        发起线索---不符合展位---进入好单客源
        """

        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID', loanId)
        with allure.step('好单客源校验'):
            time.sleep(3)
            xdd2_assert().app_source(loanId)
            print('-' * 25 + "按钮均关闭——发起线索不符合展位——进入好单客源" + '-' * 25)


@pytest.mark.usefixtures('setup_process')
@allure.feature('人工截单关闭,自动截单开启')
class Test_handleClose_autoOpen:

    @pytest.fixture(scope='function')
    def setup_function(self, crmManege, mysql):
        """
        1:开启自动截单按钮
        2:禁用所有不需电核广告(自动匹配 +非自动匹配)
        3:关闭展位
        """
        with allure.step('开启自动截单按钮'):
            crmManege.cutStatus(types=1, status=1)
        with allure.step('禁用所有不需电核广告'):
            advertList = crmManege.advertisingList(electricalStatus=0)
            for i in range(0, len(advertList)):
                advertID = advertList[i]['id']
                crmManege.openStatus(ID=advertID, isOpen='0')
        with allure.step('关闭所有展位'):
            close_booth = "update jgq.think_xzw_config_log SET `status` = 3;"
            mysql.sql_execute(close_booth)

    @allure.story('订单符合（定制非电核）广告,进入定制非电核广告')
    def test_case1(self, setup_function, appAddOrder, crmManege):
        with allure.step('创建【定制—非电核】广告 custom_no'):
            companyName = "dujun_gs_001"
            advertisingName = 'custom_no'
            customPlan = 1
            electricalStatus = 0
            ad_data = {"companyName": companyName, "advertisingName": advertisingName,
                       "electricalStatus": electricalStatus, "putCity": "全国",
                       "status": 1,
                       "suggestedPrice": 6, "requirement": {}, "noRequirement": {}, "customPlan": customPlan}
            crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID',loanId)
        with allure.step('多融客线索列表断言对应线索'):
            time.sleep(5)
            crm_general().assert_customList(loanId)
            print('-' * 20 + "订单符合（定制非电核）广告,进入定制非电核广告" + '-' * 20)

    @allure.story('订单不符合（定制非电核）广告,进入展位')
    def test_case2(self, setup_function, appAddOrder, appXdd2):
        with allure.step('开启展位'):
            appXdd2.changeStatus(config_id='1688', status=2)
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID',loanId)
        with allure.step('展位校验'):
            time.sleep(8)
            boothOrderList = appXdd2.catchOrderList(1688)
            boothOrderID = boothOrderList[0]['id']
            assert loanId == boothOrderID
            print('-' * 20 + "订单不符合（定制非电核）广告,进入展位" + '-' * 20)

    @allure.story('订单不符合（定制非电核,展位）广告,进入非定制非电核广告')
    def test_case3(self, setup_function, appAddOrder, mysql):
        with allure.step('删除多余数据'):
            sql = "delete  from crm.crm_advertising WHERE company_name = 'dujun_gs_001' and advertising_name ='custom_yes' OR advertising_name ='custom_no' OR advertising_name ='common_no';"
            mysql.sql_execute(sql)
        with allure.step('新增非定制非电核广告'):
            companyName = "dujun_gs_001"
            advertisingName = 'common_no'
            customPlan = 0
            electricalStatus = 0
            ad_data = {"companyName": companyName, "advertisingName": advertisingName,
                       "electricalStatus": electricalStatus, "putCity": "全国",
                       "status": 1,
                       "suggestedPrice": 6, "requirement": {}, "noRequirement": {}, "customPlan": customPlan}
            adId = crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID ',loanId,'广告ID',adId)
        with allure.step('多融客线索列表断言对应线索'):
            time.sleep(5)
            crm_general().assert_customList(loanId)
            print('-' * 20 + "订单符合（定制非电核）广告,成功进入展位" + '-' * 20)

    @allure.story('订单不符合（定制非电核,展位,非定制非电核）广告,进入好单客源')
    def test_case4(self, setup_function, appAddOrder):
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID ',loanId)
        with allure.step('好单客源校验'):
            time.sleep(3)
            xdd2_assert().app_source(loanId)
            print('-' * 20 + "订单不符合（定制非电核,展位,非定制非电核）广告,进入好单客源" + '-' * 20)


@pytest.mark.usefixtures('setup_process')
@allure.feature('人工截单开启，自动截单开启')
class Test_handleOPen_autoOpen:

    @pytest.fixture(scope='function')
    def setup_class(self, crmManege):
        """
        1:开启自动+手动截单按钮
        2:禁用所有不需电核广告(自动匹配 +非自动匹配)
        """
        with allure.step('开启人工+自动截单按钮'):
            crmManege.cutStatus(types=1, status=1)
            crmManege.cutStatus(types=2, status=1)
        with allure.step('新建定制需电核广告'):
            companyName = "dujun_gs_001"
            advertisingName = 'custom_yes'
            customPlan = 1
            electricalStatus = 1
            ad_data = {"companyName": companyName, "advertisingName": advertisingName,
                       "electricalStatus": electricalStatus, "putCity": "全国",
                       "status": 1,
                       "suggestedPrice": 6, "requirement": {}, "noRequirement": {}, "customPlan": customPlan}
            crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
            adID = crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
        with allure.step('新建定制不需电核广告'):
            companyName = "dujun_gs_001"
            advertisingName = 'custom_no'
            customPlan = 1
            electricalStatus = 0
            ad_data = {"companyName": companyName, "advertisingName": advertisingName,
                       "electricalStatus": electricalStatus, "putCity": "全国",
                       "status": 1,
                       "suggestedPrice": 6, "requirement": {}, "noRequirement": {}, "customPlan": customPlan}
            crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
        return adID

    @allure.story('线索符合定制需电核广告,推送定制需电核广告')
    def test_case1(self, appAddOrder, crmManege, setup_class):
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
        with allure.step("对应线索推送给符合条件广告"):
            print('线索ID：', loanId, '广告ID：', setup_class)
            time.sleep(3)
            crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
        with allure.step('多融客校验'):
            time.sleep(5)
            crm_general().assert_customList(loanId)
            print('-' * 20 + "线索符合定制需电核广告,推送定制需电核广告" + '-' * 20)

    @allure.story('线索符合定制需电核广告,手动置为电核单,进入好单客源')
    def test_case2(self, appAddOrder, crmManege,setup_class):
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
        with allure.step('CRM对应线索置为电核单'):
            time.sleep(1)
            crmManege.setOrder(loanId)
        with allure.step('进入好单客源'):
            time.sleep(3)
            xdd2_assert().app_source(loanId)
            print('-' * 20 + "线索符合定制需电核广告,手动置为电核单,进入好单客源" + '-' * 20)

    @allure.story('线索符合定制需电核广告,手动退还订单,进入定制非电核广告')
    def test_case3(self, appAddOrder, crmManege,setup_class):
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID ',loanId)
        with allure.step('退还对应订单'):
            time.sleep(1.5)
            crmManege.chargeBack(loanId)
        with allure.step('进入定制非电核广告,多融客校验'):
            time.sleep(5)
            crm_general().assert_customList(loanId)
            print('-' * 20 + "线索符合定制需电核广告,手动退还订单,进入定制非电核广告" + '-' * 20)

    @allure.story('线索不符合定制需电核广告,直接进入定制非电核广告')
    def test_case4(self, appAddOrder, crmManege,setup_class):
        with allure.step('禁用所有定制需电核广告'):
            advertList = crmManege.advertisingList(electricalStatus=1)
            for i in range(0, len(advertList)):
                advertID = advertList[i]['id']
                crmManege.openStatus(ID=advertID, isOpen='0')
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
            print('loanID ',loanId)
        with allure.step('进入定制非电核广告,多融客校验'):
            time.sleep(3)
            crm_general().assert_customList(loanId)
            print('-' * 20 + "线索符合定制需电核广告,手动退还订单,进入定制非电核广告" + '-' * 20)


@allure.feature('人工截单开启，自动截单关闭')
@pytest.mark.usefixtures('setup_process')
class Test_handleOPen_autoClose:

    @pytest.fixture(scope='class')
    def setup_class(self, crmManege):
        """
        1:开启人工截单,关闭自动截单
        2:禁用所有不需电核广告(自动匹配 +非自动匹配)
        """
        with allure.step('开启人工截单,关闭自动截单'):
            crmManege.cutStatus(types=2, status=1)
            crmManege.cutStatus(types=1, status=0)
        with allure.step('新建定制需电核广告'):
            companyName = "dujun_gs_001"
            advertisingName = 'custom_yes'
            customPlan = 1
            electricalStatus = 1
            ad_data = {"companyName": companyName, "advertisingName": advertisingName,
                       "electricalStatus": electricalStatus,
                       "putCity": "全国", "status": 1, "suggestedPrice": 6, "customPlan": customPlan, "requirement": {},
                       "noRequirement": {}, "remark": "interface"}
            adverting_ID_yes = crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
        with allure.step('新建定制不需电核广告'):
            companyName = "dujun_gs_001"
            advertisingName = 'custom_yes'
            customPlan = 1
            electricalStatus = 0
            ad_data = {"companyName": companyName, "advertisingName": advertisingName,
                       "electricalStatus": electricalStatus,
                       "putCity": "全国", "status": 1, "suggestedPrice": 6, "customPlan": customPlan, "requirement": {},
                       "noRequirement": {}, "remark": "interface"}
            adverting_ID_no = crm_general().add_Advertising(ad_data=ad_data, cpcPrice=25)
        return adverting_ID_yes, adverting_ID_no

    @allure.story('线索符合（定制需电核+定制不需电核+展位），退还订单-订单进入展位')
    def test_case1(self, appAddOrder, crmManege, appXdd2):
        with allure.step('开启展位'):
            appXdd2.changeStatus(config_id='1688', status=2)
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
        with allure.step('退还对应订单'):
            time.sleep(1.5)
            crmManege.chargeBack(loanId)
        with allure.step('展位校验'):
            time.sleep(3)
            boothOrderList = appXdd2.catchOrderList(1688)
            boothOrderID = boothOrderList[0]['id']
            assert loanId == boothOrderID
            print('-' * 20 + "线索符合（定制需电核+定制不需电核+展位），退还订单-订单进入展位" + '-' * 20)
