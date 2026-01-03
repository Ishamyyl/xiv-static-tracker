<script lang="ts">
    let { players } = $props();
</script>

{#each players as p}
    <p>{p}</p>
{/each}

<div class="flex-1 flex flex-col gap-4 p-4">
    <table class="border border-slate-100 border-solid border-collapse table table-auto w-max">
        <thead>
            <tr>
                <th>Item</th>
                <th>Drop</th>
                <th>Pages</th>
                <th>Tomes</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td>💍 Accessory</td>
                <td>1</td>
                <td>3 Ⅰ</td>
                <td>375</td>
            </tr>
            <tr>
                <td>🎩 Small</td>
                <td>2</td>
                <td>4 Ⅱ</td>
                <td>495</td>
            </tr>
            <tr>
                <td>✨ Glaze</td>
                <td>2</td>
                <td>3 Ⅱ</td>
                <td></td>
            </tr>
            <tr>
                <td>📱 Tomestone</td>
                <td>2</td>
                <td>7 🔪</td>
                <td></td>
            </tr>
            <tr>
                <td>🥼 Large</td>
                <td>3</td>
                <td>6 Ⅲ</td>
                <td>825</td>
            </tr>
            <tr>
                <td>🧵 Twine</td>
                <td>3</td>
                <td>4 Ⅲ</td>
                <td></td>
            </tr>
            <tr>
                <td>🧪 Solvent</td>
                <td>3</td>
                <td>4 Ⅲ</td>
                <td></td>
            </tr>
            <tr>
                <td>⚔ Weapon</td>
                <td>4</td>
                <td>8 Ⅳ</td>
                <td>500 + 📱 + 🧪</td>
            </tr>
        </tbody>
    </table>
</div>
