# MSPay 收银台配置对照表

收银台部门申请/下发。`product` / `appKey` / 协议 URL 写入 `PaymentManager.register`；IAP 回调 URL 填 App Store Connect。

| 配置项             | Claw                                                                           | namiWork                           |
| --------------- | ------------------------------------------------------------------------------ | ---------------------------------- |
| product         | `360clawcloud`                                                                 | `namiwork`                         |
| appKey          | `094f36fdaa92acaf363e079bd29fed38`                                             | `08a247e821eaee43d7d5d6cc462a200f` |
| serviceURL      | `https://pop.vip.360.cn/help/360clawcloud/client/vipServicesAgreement.html`    | 待收银台部门提供                           |
| subscriptionURL | `https://pop.vip.360.cn/help/360clawcloud/client/vipServicesAgreement_xf.html` | 待收银台部门提供                           |
| IAP 回调 URL（正式）  | `https://member.shouji.360.cn/v2/ios_notification_callback`                    | 同上                                 |
| IAP 回调 URL（测试）  | `https://membertest.shouji.360.cn/v2/ios_notification_callback`                | 同上                                 |

> **IAP 回调**：收银台统一 endpoint，Claw / namiWork 填 App Store Connect 时相同（按 product 在收银台侧区分，非按 URL 区分）。

## 备注

### 测试环境 Hosts（Claw / namiWork 共用，收银台下发）

```
#61.172.185.59 pop.shouji.360.cn      #测试1
#10.236.165.24 pop.vip.360.cn
#112.65.208.35 member.shouji.360.cn
#112.65.208.36 exquisite.shouji.360.cn
```
