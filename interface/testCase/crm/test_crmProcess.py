# -*- coding: utf-8 -*-
# @Time    : 2021/6/15 16:31
# @Author  : dujun
# @File    : test_crmProcess.py
# @describe: CRM管理后台
import time
import allure
import pytest
from interface.data.order_data import order_data
from interface.tools.dataBase import DataBase


@allure.feature('CRM订单分配流程-关闭截单按钮')
class Test_closeCut:

    @staticmethod
    def teardown_class():
        mysql = DataBase()
        sql = "delete  from crm.crm_advertising WHERE company_name = 'dujun_gs_001' and advertising_name ='interface_no' OR advertising_name ='interface_yes';"
        mysql.sql_execute(sql)

    @allure.story('关闭截单,均不符合(展位+不需电核广告)-->进入好单客源')
    def test_case1(self, crmManege, mysql, appAddOrder, appXdd2, crmAdmin):
        """
        登录CRM后台关闭截单按钮
        查询数据库，关闭所有开启展位
        禁用所有需电核广告
        发起线索———>进入好单客源查看对应订单
        """
        status_re = crmManege.getStatus()
        status = status_re['data']['status']
        if status:
            crmManege.cutStatus(0)
        else:
            pass
        sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
        booth = mysql.sql_execute(sql1)
        if booth:
            print('存在已开启的展位')
            sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
            mysql.sql_execute(sql2)
        else:
            print("不存在开启的展位")
        with allure.step('禁用所有不需电核广告'):
            advertList = crmManege.advertisingList(electricalStatus=0)
            for i in range(0, len(advertList)):
                advertID = advertList[i]['id']
                crmAdmin.editAdIsOpen(advertID, isOpen='false')
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
        with allure.step('好单客源校验'):
            time.sleep(1.5)
            orderList = appXdd2.orderList(520400)  # 安顺市
            i = 0
            status = False
            while i < len(orderList['data']['data']):
                if loanId == orderList['data']['data'][i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------关闭截单,均不符合(展位+不需电核广告)-->进入好单客源----------------------------')
            else:
                raise Exception("订单不在好单客源中")

    @allure.story('关闭截单,符合展位-->进入对应展位')
    def test_case2(self, crmManege, mysql, appAddOrder, appXdd2, crmAdmin):
        """
        登录CRM后台关闭截单按钮
        查询数据库，关闭所有开启展位--打开对应展位
        发起线索———>展位查询对应线索
        """
        with allure.step('登录CRM后台关闭截单按钮'):
            status_re = crmManege.getStatus()
            status = status_re['data']['status']
            if status:
                crmManege.cutStatus(0)
            else:
                pass
        with allure.step('查询数据库，关闭所有开启展位,开启对应展位'):
            sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
            booth = mysql.sql_execute(sql1)
            if booth:
                print('存在已开启的展位')
                sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
                mysql.sql_execute(sql2)
            else:
                print("不存在开启的展位")
            # 开启对应展位
            appXdd2.changeStatus(config_id='1688', status=2)
        with allure.step('信业帮发起线索请求'):
            time.sleep(1)
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            loanId = appAddOrder.get_loanId()
        with allure.step('展位校验'):
            time.sleep(1)
            boothOrderList = appXdd2.catchOrderList(1688)
            boothOrderID = boothOrderList[0]['id']
            assert loanId == boothOrderID
            print('-----------------------关闭截单,符合展位-->进入展位--------------------------')

    @allure.story('关闭截单,不符合展位，符合不需电核广告-->推送不需电核广告')
    def test_case3(self, crmManege, mysql, appAddOrder, appXdd2, crmAdmin):
        """
        关闭全部展位
        关闭所有不需电核的广告
        打开不需电核的广告，查询线索余量，不足进行充值
        查询对应广告下是否存在此订单
        """
        cpcPrice = 25
        with allure.step('登录CRM后台关闭截单按钮'):
            status_re = crmManege.getStatus()
            status = status_re['data']['status']
            if status:
                crmManege.cutStatus(0)
            else:
                pass
        with allure.step('查询数据库，关闭所有展位'):
            sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
            booth = mysql.sql_execute(sql1)
            if booth:
                print('存在已开启的展位')
                sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
                mysql.sql_execute(sql2)
            else:
                print("不存在开启的展位")
        with allure.step('禁用所有不需电核广告, 新增不需电核广告'):
            advertList = crmManege.advertisingList(electricalStatus=0)
            for i in range(0, len(advertList)):
                advertID = advertList[i]['id']
                crmAdmin.editAdIsOpen(advertID, isOpen='false')
            # 新增不需电核的广告
            Advertising_data = {"companyName": "dujun_gs_001", "advertisingName": "interface_no", "electricalStatus": 0,
                                "putCity": "安顺市", "status": 1, "suggestedPrice": 6, "requirement": {},
                                "noRequirement": {}}
            crmManege.addAdvertising(payload=Advertising_data)
            advert_list = crmManege.advertisingList(companyName="dujun_gs_001", advertisingName="interface_no",
                                                    electricalStatus=0)
            advert_id = advert_list[0]['id']
            crmAdmin.editAd(ID=advert_id, budgetConfig=999999, cpcPrice=cpcPrice)
            cpcPrice = 25
            with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
                crmAdmin.editAd(ID=advert_id, budgetConfig=99999, cpcPrice=cpcPrice)
            with allure.step('查询修改账户余额【大于CPC出价25】'):
                companyMoney = crmAdmin.detail()['data']['money']
                if companyMoney < cpcPrice:
                    crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
            with allure.step('查询修改账户剩余日预算【大于CPC出价25】'):
                crmAdmin.update(999999)
            with allure.step('查询修改广告日预算【大于CPC出价25】'):
                crmAdmin.editAd(ID=advert_id, budgetConfig=99999, cpcPrice=cpcPrice)
            # 信业帮发起线索
            with allure.step('信业帮发起线索请求'):
                payload = order_data(city_name='安顺市')
                appAddOrder.app_addOrder(payload)
                # 线索ID
                loanId = appAddOrder.get_loanId()
            with allure.step('不需电核广告校验'):
                print(advert_id, loanId)
                time.sleep(2)
                clientList = crmAdmin.customerList(adName='interface_no')
                i = 0
                status = False
                while i < len(clientList):
                    if loanId == clientList[i]['id']:
                        status = True
                        break
                    else:
                        i += 1
                if status is True:
                    print('----------------------条件均符合,正常推送到不需电核广告--------------------------')
                else:
                    raise Exception("线索", loanId, "不在interface_no广告中")


@allure.feature("CRM订单分配流程-开启截单按钮")
class Test_openCut:

    @staticmethod
    def teardown_class():
        mysql = DataBase()
        sql = "delete  from crm.crm_advertising WHERE company_name = 'dujun_gs_001' and advertising_name ='interface_no' OR advertising_name ='interface_yes';"
        mysql.sql_execute(sql)

    @pytest.fixture(scope='class')
    def setup_class(self, crmManege, crmAdmin):
        """
        1：开启截单按钮 2：新增需电核广告
        :return: 广告ID
        """
        # 开启截单按钮
        with allure.step('登录CRM后台开启截单按钮'):
            status_re = crmManege.getStatus()
            status = status_re['data']['status']
            if status:
                pass
            else:
                crmManege.cutStatus(1)
        with allure.step('CRM添加需电核的广告,条件不限制'):
            Advertising_data = {"companyName": "dujun_gs_001", "advertisingName": "interface_yes",
                                "electricalStatus": 1,
                                "putCity": "安顺市", "status": 1, "suggestedPrice": 6, "requirement": {},
                                "noRequirement": {}}
            crmManege.addAdvertising(payload=Advertising_data)

            advert_list = crmManege.advertisingList(companyName="dujun_gs_001", advertisingName="interface_yes",
                                                    electricalStatus=1)
            # 广告ID
            advert_id = advert_list[0]['id']
            crmAdmin.editAd(ID=advert_id, budgetConfig=99999, cpcPrice=25)

        return advert_id

    @allure.story('开启截单,CRM置为电核单--->进入好单客源')
    def test_case1(self, crmManege, appXdd2, setup_class, appAddOrder):
        """
        CRM置位电核单
        推送好单客源，断言
        """
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        # 对应线索置为电核单
        with allure.step('CRM对应线索置为电核单'):
            time.sleep(1)
            crmManege.setOrder(loanId)

        # 订单ID是否在好单客源
        with allure.step('好单客源校验'):
            time.sleep(1.5)
            orderList = appXdd2.orderList(520400)  # 安顺市
            i = 0
            status = False
            while i < len(orderList['data']['data']):
                if loanId == orderList['data']['data'][i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------开启截单,CRM置为电核单--->进入好单客源----------------------------')
            else:
                raise Exception("订单不在好单客源中")

    @allure.story('开启截单,符合需电核的广告--->推送对应广告')
    def test_case2(self, appAddOrder, setup_class, crmAdmin, crmManege):
        """
        线索推送对应需电核广告
        需电核广告断言
        """
        cpcPrice = 25
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=99999, cpcPrice=cpcPrice)
        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户剩余日预算【大于CPC出价25】'):
            crmAdmin.update(999999)
        with allure.step('查询修改广告日预算【大于CPC出价25】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=99999, cpcPrice=cpcPrice)

        with allure.step("对应线索推送给符合条件广告"):
            crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
        with allure.step('查询对应广告下是否存在此订单'):
            clientList = crmAdmin.customerList(adName='interface_yes')
            i = 0
            status = False
            while i < len(clientList):
                if loanId == clientList[i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------开启截单,推送需电核的广告---->多融客-------------------------')
            else:
                raise Exception("线索", loanId, "不在interface_yes广告中")

    @allure.story('开启截单,----退还订单---->好单客源')
    def test_case3(self, appAddOrder, setup_class, crmAdmin, mysql, crmManege, appXdd2):
        with allure.step('关闭所有展位'):
            sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
            booth = mysql.sql_execute(sql1)
            if booth:
                print('存在已开启的展位')
                sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
                mysql.sql_execute(sql2)
            else:
                print("不存在开启的展位")
        with allure.step('禁用所有不需电核广告'):
            advertList = crmManege.advertisingList(electricalStatus=0)
            for i in range(0, len(advertList)):
                advertID = advertList[i]['id']
                crmAdmin.editAdIsOpen(advertID, isOpen='false')
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('退还对应订单'):
            crmManege.chargeBack(loanId)
            # 订单ID是否在好单客源
            with allure.step('好单客源校验'):
                time.sleep(1.5)
                orderList = appXdd2.orderList(520400)  # 安顺市
                i = 0
                status = False
                while i < len(orderList['data']['data']):
                    if loanId == orderList['data']['data'][i]['id']:
                        status = True
                        break
                    else:
                        i += 1
                if status is True:
                    print('-----------------------开启截单----退还订单---->好单客源----------------------------')
                else:
                    raise Exception("订单不在好单客源中")

    @allure.story('开启截单----退还订单---->进入展位')
    def test_case4(self, appAddOrder, setup_class, crmAdmin, mysql, crmManege, appXdd2):
        with allure.step('关闭所有展位'):
            sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
            booth = mysql.sql_execute(sql1)
            if booth:
                print('存在已开启的展位')
                sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
                mysql.sql_execute(sql2)
            else:
                print("不存在开启的展位")
            # 开启对应展位
            appXdd2.changeStatus(config_id='1688', status=2)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            time.sleep(1)
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
            print('loanId', loanId)
        with allure.step('退还对应订单'):
            time.sleep(1)
            crmManege.chargeBack(loanId)
        with allure.step('展位校验'):
            time.sleep(1)
            boothOrderList = appXdd2.catchOrderList(1688)
            print(boothOrderList)
            boothOrderID = boothOrderList[0]['id']
            assert loanId == boothOrderID
            print('-----------------------开启截单----退还订单---->进入展位--------------------------')

    # @allure.story('开启截单,符合需电核的广告----退还订单---->进入无需电核广告')
    # def test_case5(self, appAddOrder, setup_class, crmAdmin, mysql, crmManege, appXdd2):
    #     with allure.step('关闭所有展位'):
    #         sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
    #         booth = mysql.sql_execute(sql1)
    #         if booth:
    #             print('存在已开启的展位')
    #             sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
    #             mysql.sql_execute(sql2)
    #         else:
    #             print("不存在开启的展位")
    #     cpcPrice = 25


@allure.feature("线索--->需电核广告,价格余额逻辑判断")
class Test_priceLogic_callBack:

    @pytest.fixture(scope='class')
    def setup_class(self, crmManege, crmAdmin, mysql):
        """
        1：开启截单按钮 2：新增需电核广告
        :return: 广告ID
        """
        sql = "delete  from crm.crm_advertising WHERE company_name = 'dujun_gs_001' and advertising_name ='interface_no' OR advertising_name ='interface_yes';"
        mysql.sql_execute(sql)
        # 开启截单按钮
        with allure.step('登录CRM后台开启截单按钮'):
            status_re = crmManege.getStatus()
            status = status_re['data']['status']
            if status:
                pass
            else:
                crmManege.cutStatus(1)
        with allure.step('CRM添加需电核的广告,条件不限制'):
            Advertising_data = {"companyName": "dujun_gs_001", "advertisingName": "interface_yes",
                                "electricalStatus": 1,
                                "putCity": "安顺市", "status": 1, "suggestedPrice": 6, "requirement": {},
                                "noRequirement": {}}
            crmManege.addAdvertising(payload=Advertising_data)

            advert_list = crmManege.advertisingList(companyName="dujun_gs_001", advertisingName="interface_yes",
                                                    electricalStatus=1)
            # 广告ID
            advert_id = advert_list[0]['id']
        return advert_id

    @allure.story("CPC出价小于建议出价，不能推单")
    def test_case1(self, setup_class, crmAdmin, appAddOrder, crmManege):
        with allure.step('多融客修改对应广告信息'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=999999, cpcPrice=1)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('线索推送给对应广告'):
            pushRes = crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
            msg = pushRes['msg']
            message = 'CPC出价小于建议出价，不能推单'
            assert msg == message

    @allure.story("账户余额不足，不能推单")
    def test_case2(self, setup_class, crmAdmin, appAddOrder, crmManege):
        cpcPrice = 25
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=999999, cpcPrice=cpcPrice)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('关闭所有广告'):
            advertList = crmManege.advertisingList(companyName='dujun_gs_001', electricalStatus=1)
            for i in range(len(advertList)):
                crmManege.openStatus(ID=advertList[i]['id'], isOpen=0)

        with allure.step('查询修改账户余额【小于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney - cpcPrice >= 0:
                crmManege.refund(companyName='dujun_gs_001', threadMoney=companyMoney - cpcPrice)
            else:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice - companyMoney)

        with allure.step('打开所有广告'):
            for i in range(len(advertList)):
                crmManege.openStatus(ID=advertList[i]['id'], isOpen=1)
        with allure.step('线索推送给对应广告'):
            time.sleep(1)
            crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
            payload = order_data(city_name='安顺市')
            time.sleep(1)
            appAddOrder.app_addOrder(payload)
            loanId2 = appAddOrder.get_loanId()
            pushRes = crmManege.push(advertisingId=setup_class, thinkLoanId=loanId2, companyName='dujun_gs_001')
            print(pushRes)
            message = '账户余额不足，不能推单'
            assert message == pushRes['msg']

    @allure.story("账户剩余日预算不足，不能推单")
    def test_case3(self, setup_class, crmAdmin, appAddOrder, crmManege):
        cpcPrice = 25
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=999999, cpcPrice=cpcPrice)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()

        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户日预算【小于CPC出价25】'):
            crmAdmin.update(cpcPrice - 5)
        with allure.step('线索推送给对应广告'):
            pushRes = crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
            msg = pushRes['msg']
            message = '账户剩余日预算不足，不能推单'
            assert message == msg

    @allure.story("广告剩余预算小于CPC出价，不能推单")
    def test_case4(self, setup_class, crmAdmin, appAddOrder, crmManege):
        cpcPrice = 25
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=999999, cpcPrice=cpcPrice)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()

        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户剩余日预算【大于CPC出价25】'):
            crmAdmin.update(999999)
        with allure.step('查询修改广告日预算【小于CPC出价25】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=cpcPrice - 5, cpcPrice=cpcPrice)
        with allure.step('线索推送给对应广告'):
            time.sleep(1)
            pushRes = crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
            msg = pushRes['msg']
            message = '广告剩余预算小于CPC出价，不能推单'
            assert message == msg

    @allure.story("条件均符合,可正常推送广告")
    def test_case5(self, setup_class, crmAdmin, appAddOrder, crmManege):
        """
        广告CPC出价 大于 建议出价
        账户余额大于CPC出价
        账户剩余日预算大于 CPC出价
        广告剩余日预算大于CPC出价
        """
        cpcPrice = 25
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=99999, cpcPrice=cpcPrice)
        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户剩余日预算【大于CPC出价25】'):
            crmAdmin.update(999999)
        with allure.step('查询修改广告日预算【大于CPC出价25】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=99999, cpcPrice=cpcPrice)
        with allure.step('线索推送给对应广告'):
            print(setup_class, loanId)
            time.sleep(1)
            pushRes = crmManege.push(advertisingId=setup_class, thinkLoanId=loanId, companyName='dujun_gs_001')
            message = '操作成功！'
            msg = pushRes['msg']
            assert msg == message
            clientList = crmAdmin.customerList(adName='interface_yes')
            i = 0
            status = False
            while i < len(clientList):
                if loanId == clientList[i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------开启截单,推送需电核的广告---->多融客-------------------------')
            else:
                raise Exception("线索", loanId, "不在interface_yes广告中")


@allure.feature("线索--->不需电核广告,价格余额逻辑判断")
class Test_priceLogic_NoCallBack:

    @pytest.fixture(scope='class')
    def setup_class(self, crmManege, crmAdmin, mysql):
        """
        1：关闭截单按钮  2：关闭所有展位  3：新增不需电核广告
        :return: 广告ID
        """
        sql = "delete  from crm.crm_advertising WHERE company_name = 'dujun_gs_001' and advertising_name ='interface_no' OR advertising_name ='interface_yes';"
        mysql.sql_execute(sql)
        with allure.step('登录CRM后台关闭截单按钮'):
            status_re = crmManege.getStatus()
            status = status_re['data']['status']
            if status:
                crmManege.cutStatus(0)
            else:
                pass
        with allure.step('查询数据库，关闭所有展位'):
            sql1 = "SELECT * FROM jgq.think_xzw_config_log WHERE `status` = 2;"
            booth = mysql.sql_execute(sql1)
            if booth:
                print('存在已开启的展位')
                sql2 = "update jgq.think_xzw_config_log SET `status` = 3;"
                mysql.sql_execute(sql2)
            else:
                print("不存在开启的展位")
        with allure.step('禁用所有不需电核广告, 新增不需电核广告'):
            advertList = crmManege.advertisingList(electricalStatus=0)
            for i in range(0, len(advertList)):
                advertID = advertList[i]['id']
                crmAdmin.editAdIsOpen(advertID, isOpen='false')
            # 新增不需电核的广告
            Advertising_data = {"companyName": "dujun_gs_001", "advertisingName": "interface_no", "electricalStatus": 0,
                                "putCity": "安顺市", "status": 1, "suggestedPrice": 6, "requirement": {},
                                "noRequirement": {}}
            crmManege.addAdvertising(payload=Advertising_data)
            advert_list = crmManege.advertisingList(companyName="dujun_gs_001", advertisingName="interface_no",
                                                    electricalStatus=0)
            advert_id = advert_list[0]['id']
            crmAdmin.editAd(ID=advert_id, budgetConfig=99999, cpcPrice=25)
        return advert_id

    @allure.story("CPC出价小于建议出价，进入好单客源")
    def test_case1(self, setup_class, crmAdmin, appAddOrder, appXdd2):
        with allure.step('多融客修改对应广告信息'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=999999, cpcPrice=1)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('好单客源校验'):
            time.sleep(1.5)
            orderList = appXdd2.orderList(520400)  # 安顺市
            i = 0
            status = False
            while i < len(orderList['data']['data']):
                if loanId == orderList['data']['data'][i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------CPC出价小于建议出价，进入好单客源----------------------------')
            else:
                raise Exception("订单不在好单客源中")

    @allure.story("账户剩余日预算不足--好单客源")
    def test_case3(self, setup_class, crmAdmin, appAddOrder, appXdd2, crmManege):
        cpcPrice = 25
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=9999999, cpcPrice=cpcPrice)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()

        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户日预算【小于CPC出价25】'):
            crmAdmin.update(cpcPrice - 5)
        with allure.step('好单客源校验'):
            time.sleep(1.5)
            orderList = appXdd2.orderList(520400)  # 安顺市
            i = 0
            status = False
            while i < len(orderList['data']['data']):
                if loanId == orderList['data']['data'][i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------账户剩余日预算不足--好单客源----------------------------')
            else:
                raise Exception("订单不在好单客源中")

    @allure.story("广告剩余预算小于CPC出价---->好单客源")
    def test_case4(self, setup_class, crmAdmin, appAddOrder, crmManege, appXdd2):
        cpcPrice = 25
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=999999, cpcPrice=cpcPrice)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()

        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户剩余日预算【大于CPC出价25】'):
            crmAdmin.update(999999)
        with allure.step('查询修改广告日预算【小于CPC出价25】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=cpcPrice - 5, cpcPrice=cpcPrice)
        with allure.step('好单客源校验'):
            time.sleep(1.5)
            orderList = appXdd2.orderList(520400)  # 安顺市
            i = 0
            status = False
            while i < len(orderList['data']['data']):
                if loanId == orderList['data']['data'][i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('-----------------------广告剩余预算小于CPC出价---->好单客源----------------------------')
            else:
                raise Exception("订单不在好单客源中")

    @allure.story("条件均符合,正常推送到不需电核广告")
    def test_case5(self, setup_class, crmAdmin, appAddOrder, crmManege):
        """
        广告CPC出价 大于 建议出价
        账户余额大于CPC出价
        账户剩余日预算大于 CPC出价
        广告剩余日预算大于CPC出价
        """
        cpcPrice = 25
        with allure.step('多融客修改对应广告信息【CPC大于 建议出价】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=99999, cpcPrice=cpcPrice)
        with allure.step('查询修改账户余额【大于CPC出价25】'):
            companyMoney = crmAdmin.detail()['data']['money']
            if companyMoney < cpcPrice:
                crmManege.recharge(companyName='dujun_gs_001', threadMoney=cpcPrice)
        with allure.step('查询修改账户剩余日预算【大于CPC出价25】'):
            crmAdmin.update(999999)
        with allure.step('查询修改广告日预算【大于CPC出价25】'):
            crmAdmin.editAd(ID=setup_class, budgetConfig=99999, cpcPrice=cpcPrice)
        # 信业帮发起线索
        with allure.step('信业帮发起线索请求'):
            payload = order_data(city_name='安顺市')
            appAddOrder.app_addOrder(payload)
            # 线索ID
            loanId = appAddOrder.get_loanId()
        with allure.step('不需电核广告校验'):
            print(setup_class, loanId)
            time.sleep(2)
            clientList = crmAdmin.customerList(adName='interface_no')
            i = 0
            status = False
            while i < len(clientList):
                if loanId == clientList[i]['id']:
                    status = True
                    break
                else:
                    i += 1
            if status is True:
                print('----------------------条件均符合,正常推送到不需电核广告--------------------------')
            else:
                raise Exception("线索", loanId, "不在interface_no广告中")