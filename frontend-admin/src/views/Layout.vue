<template>
  <el-container style="min-height: 100vh">
    <el-aside width="200px">
      <div class="logo">BeCool Market</div>
      <el-menu
        :default-active="route.path"
        router
        background-color="#001529"
        text-color="#ffffffcc"
        active-text-color="#ff4400"
      >
        <el-menu-item index="/products">
          <el-icon><Goods /></el-icon>
          <span>商品管理</span>
        </el-menu-item>
        <el-menu-item index="/categories">
          <el-icon><Menu /></el-icon>
          <span>分类管理</span>
        </el-menu-item>
        <el-menu-item index="/countries">
          <el-icon><Flag /></el-icon>
          <span>国家管理</span>
        </el-menu-item>
        <el-menu-item index="/orders">
          <el-icon><ShoppingCart /></el-icon>
          <span>订单管理</span>
        </el-menu-item>
        <el-menu-item index="/gdpr">
          <el-icon><Document /></el-icon>
          <span>GDPR 请求</span>
        </el-menu-item>
        <el-menu-item index="/flash-deals">
          <el-icon><Timer /></el-icon>
          <span>闪购管理</span>
        </el-menu-item>
        <el-menu-item index="/banners">
          <el-icon><Picture /></el-icon>
          <span>Banner 管理</span>
        </el-menu-item>
        <el-menu-item index="/shipping-methods">
          <el-icon><Van /></el-icon>
          <span>派送方式</span>
        </el-menu-item>
        <el-menu-item index="/shipping-origins">
          <el-icon><Location /></el-icon>
          <span>发货地</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="header">
        <span>BeCool Market 管理后台</span>
        <el-dropdown @command="handleCommand">
          <span class="user-info">
            {{ auth.user?.display_name || '管理员' }}
            <el-icon><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { Goods, Menu, Document, ArrowDown, ShoppingCart, Timer, Picture, Van, Location, Flag } from '@element-plus/icons-vue'
import { useAuthStore } from '../store/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const handleCommand = (cmd) => {
  if (cmd === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  font-weight: 800;
  color: #ff4400;
  background: #001529;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.user-info {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}
</style>
