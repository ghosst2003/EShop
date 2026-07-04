<template>
  <div class="login-page">
    <el-card class="login-card">
      <h2>BeCool Market 管理后台</h2>
      <el-form :model="form" @submit.prevent="handleLogin">
        <el-form-item>
          <el-input v-model="form.username" placeholder="用户名" prefix-icon="User" size="large" />
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password" type="password" placeholder="密码" prefix-icon="Lock" size="large" show-password />
        </el-form-item>
        <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">
          登录
        </el-button>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login, getMe } from '../api'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const auth = useAuthStore()
const loading = ref(false)
const form = reactive({ username: '', password: '' })

const handleLogin = async () => {
  loading.value = true
  try {
    const { data } = await login(form.username, form.password)
    auth.setToken(data.access_token)
    const { data: user } = await getMe()
    auth.setUser(user)
    ElMessage.success('登录成功')
    router.push('/')
  } catch (e) {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background: #f2f3f7;
}
.login-card {
  width: 360px;
  text-align: center;
}
.login-card h2 {
  margin-bottom: 24px;
  color: #ff4400;
}
</style>
