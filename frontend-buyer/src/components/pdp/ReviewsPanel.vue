<template>
  <div class="py-6 text-center">
    <div class="text-5xl mb-4">💬</div>
    <h3 class="text-lg font-semibold text-gray-700 mb-2">No reviews yet</h3>
    <p class="text-sm text-gray-400">Be the first to review this product!</p>
    <!-- Structured for future API integration:
         Expected API: GET /api/products/:slug/reviews
         Returns: { average_rating, review_count, rating_distribution, reviews: [{ rating, comment, user_name, created_at, images }] }
    -->
  </div>
</template>

<script setup>
// Mock reviews placeholder — wire up to API when backend supports reviews
</script>
