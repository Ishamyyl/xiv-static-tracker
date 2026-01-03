<script lang="ts">
    let { desired, current } = $props();
</script>

{#each desired as d}
    <p>{d}</p>
{/each}

{#each current as c}
    <p>{c}</p>
{/each}
