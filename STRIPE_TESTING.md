# Stripe 测试指南

项目使用 Stripe 托管的 Checkout 页面。银行卡信息不会经过或保存在本系统中。

## 1. 获取测试密钥

1. 登录 Stripe Dashboard，切换到 **Sandbox / Test mode**。
2. 在 **Developers → API keys** 复制测试 Secret key（`sk_test_...`）。
3. 不要把密钥提交到 Git，也不要在聊天或截图中发送密钥。

编辑 `backend/.env`：

```dotenv
FRONTEND_URL=http://127.0.0.1:5175
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...
```

修改后必须重启 Python 后端。

## 2. 本地 Webhook

本机地址不能直接接收 Stripe 的公网回调，需要 Stripe CLI：

```bash
stripe login
stripe listen \
  --events checkout.session.completed,checkout.session.expired,checkout.session.async_payment_failed,payment_intent.payment_failed \
  --forward-to http://127.0.0.1:8000/api/payments/webhook
```

CLI 启动后会显示 `whsec_...`。将它填入 `backend/.env` 的
`STRIPE_WEBHOOK_SECRET`，然后重启后端。CLI 必须在测试期间保持运行。

后端手工启动：

```bash
cd /path/to/ESHShop
python3 start_server.py
```

## 3. 公网服务器 Webhook

在 Stripe Dashboard 的 **Developers / Workbench → Webhooks** 创建端点：

```text
https://icoolps.com/api/payments/webhook
```

订阅：

- `checkout.session.completed`
- `checkout.session.expired`
- `checkout.session.async_payment_failed`
- `payment_intent.payment_failed`

复制该端点的 Signing secret（`whsec_...`）到服务器的
`backend/.env`，然后重启后端。测试环境和正式环境的 `whsec_...` 不能混用。

## 4. 完整测试流程

1. 后台新增或编辑商品，将交易方式设为“在线支付”，并保证库存大于 0。
2. 客户端登录已验证邮箱的买家账号。
3. 只勾选在线支付商品，进入结算页并选择收货地址。
4. 同意条款并点击在线支付，系统会创建待付款订单并跳转 Stripe Checkout。
5. 使用 Stripe 测试卡，不要使用真实银行卡：

| 场景 | 卡号 | 其他信息 |
| --- | --- | --- |
| 支付成功 | `4242 4242 4242 4242` | 任意未来日期、任意 3 位 CVC |
| 需要 3DS | `4000 0000 0000 3220` | 任意未来日期、任意 3 位 CVC |
| 余额不足 | `4000 0000 0000 9995` | 任意未来日期、任意 3 位 CVC |

成功支付后应自动返回订单结果页。Webhook 到达后，订单应变为 `paid`，
`payment_status` 应为 `paid`，库存预留应转为已扣减状态。失败或过期时，订单不能变为已付款，库存预留应释放。

## 5. 查看测试日志

本地运行时直接查看启动后端和 `stripe listen` 的两个终端。服务器使用 systemd 时：

```bash
sudo journalctl -u eshshop -f
```

Stripe Dashboard 的 Webhook 端点页面也会显示每次投递的 HTTP 状态和响应。

