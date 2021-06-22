# -*- coding: utf-8 -*-
# @Time    : 2021/6/7 10:49
# @Author  : dujun
# @File    : test_crmProcess.py
# @describe:

from interface.data.CRM_Account import username, account
from interface.project.crm.manage import crm_pro


class crm_manage:

    def __init__(self, loginName, env=''):
        self.crm = crm_pro(environment=env)
        payload = account(user=loginName)
        re = self.crm.crm_login(datas=payload)
        self.token = re['data']['token']
        self.headers = {
            'Content-Type': 'application/json',
            'token': self.token
        }

    # CRM广告列表_修改广告
    def updateAdvertising(self, ID):
        """
        :param ID: 广告ID
        electricalStatus:是否电核 0 不需电核 1需电核
        status ： 0 禁用  1 启用
        """
        payload = {"companyName": "dujun_gs_001", "advertisingName": "interface_01", "electricalStatus": 0,
                   "putCity": "安顺市",
                   "status": 1, "requirement": {}, "noRequirement": {}, "id": ID}
        re = self.crm.updateAdvertising(headers=self.headers, datas=payload)
        print('CRM广告列表_修改广告', re)
        return re

    # 截单_待分配列表
    def undistributed(self):
        header_data = {
            'token': self.token
        }
        re = self.crm.undistributed(headers=header_data)
        print('截单_待分配列表', re)
        # ID = re['data']['records'][0]['id']
        # return ID

    # 截单_待分配列表-退还订单
    def chargeBack(self, thinkLoanId):
        """
        :param thinkLoanId: 订单ID
        """
        payload = {
            "thinkLoanId": thinkLoanId
        }
        self.crm.chargeBack(headers=self.headers, datas=payload)

    # 待分配列表-查询按钮状态(截单按钮)
    def getStatus(self):
        headers = {
            'token': self.token
        }
        res = self.crm.getStatus(headers=headers)
        return res

    # crm添加广告
    def addAdvertising(self, payload):
        # payload = {
        #     "companyName": '',  # 公司名称
        #     "advertisingName": 'advertisingName',  # 广告名称
        #     "electricalStatus": 'electricalStatus',  # 是否电核 1:电核 0:非电核
        #     "putCity": 'putCity',  # 城市
        #     "status": 'status',  # 是否启用 1:启用  0:禁用
        #     "suggestedPrice": 建议出价
        #     "requirement": {
        #     },
        #     "noRequirement": {
        #     }
        # }
        self.crm.addAdvertising(headers=self.headers, datas=payload)

    # 更新截单按钮状态
    def cutStatus(self, status):
        """
        :param status: 0:关闭  1：开启
        """
        payload = {
            "status": status
        }
        res = self.crm.cutStatus(headers=self.headers, datas=payload)
        return res

    # 查询广告列表
    def advertisingList(self, companyName='', advertisingName='', electricalStatus=None):
        """
        :param advertisingName: 广告名称
        :param companyName: 公司名称
        :param electricalStatus: 是否电核 0 非电核  1：电核
        """
        payload = {
            'electricalStatus': electricalStatus,
            'companyName': companyName,
            'advertisingName': advertisingName,

        }
        res = self.crm.advertisingList(headers=self.headers, params=payload)
        advertList = res['data']['records']
        return advertList

    # 待分配列表--置位电核单
    def setOrder(self, ID):
        payload = {
            "id": ID
        }
        res = self.crm.setOrder(headers=self.headers, datas=payload)
        return res

    # CRM-充值-余额
    def recharge(self, companyName, threadMoney):
        payload = {
            "companyName": companyName,
            "threadMoney": threadMoney
        }
        res = self.crm.recharge(headers=self.headers, datas=payload)
        return res

    # CRM-退款-余额
    def refund(self, companyName, threadMoney):
        payload = {
            "companyName": companyName,
            "threadMoney": threadMoney
        }
        res = self.crm.refund(headers=self.headers, datas=payload)
        return res


if __name__ == "__main__":
    run = crm_manage(username['管理员'], env='')
    # datas = {"companyName":"dujun_gs_001","advertisingName":"interface_no","electricalStatus":0,"putCity":"安顺市","status":1,"requirement":{},"noRequirement":{}}
    # run.addAdvertising(datas)
    run.chargeBack(10518)
