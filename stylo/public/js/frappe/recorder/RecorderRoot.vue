<template>
	<keep-alive include="RecorderDetail">
		<router-view />
	</keep-alive>
</template>

<script>
export default {
	name: "RecorderRoot",
	watch: {
		async $route() {
			stylo.router.current_route = await stylo.router.parse();
			stylo.breadcrumbs.update();
		},
	},
};
</script>
