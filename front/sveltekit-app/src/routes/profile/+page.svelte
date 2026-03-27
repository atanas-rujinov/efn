<script lang="ts">
	import { auth } from '$lib/stores/auth';
	import { driversApi, disabledApi } from '$lib/api/entities';
	import { notifications } from '$lib/stores/notifications';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';

	const user = auth.user;

	let name = '';
	let phone = '';
	let disability = '';
	let saving = false;
	let loading = true;
	let editMode = false;

	// Snapshot to allow cancel
	let snapshot = { name: '', phone: '', disability: '' };

	onMount(() => {
		const unsub = auth.isAuthenticated.subscribe((val) => {
			if (!val) goto('/login');
		});

		const unsubUser = user.subscribe((u) => {
			if (u) {
				name = u.name ?? '';
				phone = (u as any).phone ?? '';
				disability = u.disability ?? '';
				loading = false;
			}
		});

		return () => { unsub(); unsubUser(); };
	});

	function startEdit() {
		snapshot = { name, phone, disability };
		editMode = true;
	}

	function cancelEdit() {
		name = snapshot.name;
		phone = snapshot.phone;
		disability = snapshot.disability;
		editMode = false;
	}

	async function save() {
		if (!$user) return;
		saving = true;
		try {
			const payload: Record<string, string> = { name, phone };
			if ($user.role === 'disabled') payload.disability = disability;

			const api = $user.role === 'driver' ? driversApi : disabledApi;
			const updated = await api.update($user.id, payload);

			// Sync auth store with new values
			auth.setUser({ ...$user, ...updated } as any);
			notifications.success('Profile updated!');
			editMode = false;
		} catch (e) {
			console.error(e);
			notifications.error('Could not save profile.');
		} finally {
			saving = false;
		}
	}

	$: initial = ($user?.name ?? '?').charAt(0).toUpperCase();
	$: roleLabel = $user?.role === 'driver' ? 'Volunteer Driver' : 'Passenger';
</script>

<div class="shell">
	<nav class="nav">
		<div class="nav__logo">
			<span class="nav__mark">◆</span>
			<span class="nav__name">AccessRide</span>
		</div>
		<div class="nav__links">
			<a href="/" class="nav__back">← Dashboard</a>
			<button class="nav__logout" on:click={auth.logout}>Log out</button>
		</div>
	</nav>

	<main class="main">
		{#if loading}
			<div class="loading-state">
				<div class="spinner"></div>
				<p>Loading profile…</p>
			</div>
		{:else if $user}
			<div class="profile-layout">

				<!-- Left: identity card -->
				<aside class="identity-card">
					<div class="avatar">{initial}</div>
					<div class="identity-info">
						<h1 class="identity-name">{$user.name}</h1>
						<span class="role-badge role-badge--{$user.role}">{roleLabel}</span>
					</div>
					<div class="identity-meta">
						<div class="meta-row">
							<span class="meta-label">Email</span>
							<span class="meta-value">{$user.email}</span>
						</div>
						{#if $user.role === 'disabled' && $user.disability}
							<div class="meta-row">
								<span class="meta-label">Disability</span>
								<span class="meta-value">{$user.disability}</span>
							</div>
						{/if}
					</div>
				</aside>

				<!-- Right: edit form -->
				<section class="form-card">
					<div class="form-card__header">
						<h2>Profile Details</h2>
						{#if !editMode}
							<button class="btn-edit" on:click={startEdit}>Edit</button>
						{/if}
					</div>

					<div class="fields">
						<div class="field">
							<label for="name">Full Name</label>
							{#if editMode}
								<input id="name" type="text" bind:value={name} placeholder="Your name" />
							{:else}
								<p class="field-value">{name || '—'}</p>
							{/if}
						</div>

						<div class="field">
							<label for="phone">Phone Number</label>
							{#if editMode}
								<input id="phone" type="tel" bind:value={phone} placeholder="+1 555 000 0000" />
							{:else}
								<p class="field-value">{phone || '—'}</p>
							{/if}
						</div>

						{#if $user.role === 'disabled'}
							<div class="field">
								<label for="disability">Disability / Accessibility Needs</label>
								{#if editMode}
									<textarea
										id="disability"
										rows="3"
										bind:value={disability}
										placeholder="Describe your disability or accessibility needs so volunteers can best assist you…"
									></textarea>
								{:else}
									<p class="field-value">{disability || '—'}</p>
								{/if}
							</div>
						{/if}
					</div>

					{#if editMode}
						<div class="form-actions">
							<button class="btn-cancel" on:click={cancelEdit} disabled={saving}>Cancel</button>
							<button class="btn-save" on:click={save} disabled={saving}>
								{saving ? 'Saving…' : 'Save Changes'}
							</button>
						</div>
					{/if}
				</section>

			</div>
		{/if}
	</main>
</div>

<style>
	.shell { min-height: 100vh; display: flex; flex-direction: column; background: var(--bg-body); }

	/* Nav */
	.nav { display: flex; justify-content: space-between; align-items: center; padding: 1.25rem 2rem; border-bottom: 1px solid var(--border); background: var(--bg-card); }
	.nav__logo { display: flex; align-items: center; gap: 0.5rem; }
	.nav__mark { color: var(--accent); }
	.nav__name { font-family: var(--font-display); font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase; }
	.nav__links { display: flex; align-items: center; gap: 1rem; }
	.nav__back { color: var(--text-secondary); font-size: 0.875rem; text-decoration: none; }
	.nav__back:hover { color: var(--text-primary); }
	.nav__logout { background: none; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.5rem 1rem; border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer; }

	/* Layout */
	.main { flex: 1; padding: 3rem 2rem; max-width: 900px; margin: 0 auto; width: 100%; }
	.profile-layout { display: grid; grid-template-columns: 280px 1fr; gap: 2rem; align-items: start; }
	@media (max-width: 700px) { .profile-layout { grid-template-columns: 1fr; } }

	/* Loading */
	.loading-state { display: flex; flex-direction: column; align-items: center; gap: 1rem; padding: 4rem; color: var(--text-secondary); }
	.spinner { width: 2rem; height: 2rem; border: 2px solid var(--border); border-top-color: var(--accent); border-radius: 50%; animation: spin 0.7s linear infinite; }
	@keyframes spin { to { transform: rotate(360deg); } }

	/* Identity card */
	.identity-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem 1.5rem; display: flex; flex-direction: column; align-items: center; gap: 1rem; text-align: center; }
	.avatar { width: 5rem; height: 5rem; border-radius: 50%; background: var(--accent); color: #fff; display: flex; align-items: center; justify-content: center; font-size: 2rem; font-weight: 800; flex-shrink: 0; }
	.identity-info { display: flex; flex-direction: column; align-items: center; gap: 0.5rem; }
	.identity-name { font-family: var(--font-display); font-size: 1.25rem; font-weight: 700; margin: 0; }
	.role-badge { display: inline-block; padding: 0.25rem 0.75rem; border-radius: 999px; font-size: 0.75rem; font-weight: 700; }
	.role-badge--driver { background: #dbeafe; color: #1d4ed8; }
	.role-badge--disabled { background: #d1fae5; color: #065f46; }
	.identity-meta { width: 100%; display: flex; flex-direction: column; gap: 0.75rem; border-top: 1px solid var(--border); padding-top: 1rem; }
	.meta-row { display: flex; flex-direction: column; gap: 0.2rem; text-align: left; }
	.meta-label { font-size: 0.7rem; text-transform: uppercase; font-weight: 700; color: var(--text-secondary); }
	.meta-value { font-size: 0.875rem; color: var(--text-primary); word-break: break-all; }

	/* Form card */
	.form-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); padding: 2rem; display: flex; flex-direction: column; gap: 1.5rem; }
	.form-card__header { display: flex; justify-content: space-between; align-items: center; }
	.form-card__header h2 { font-family: var(--font-display); font-size: 1.1rem; font-weight: 700; margin: 0; }

	/* Fields */
	.fields { display: flex; flex-direction: column; gap: 1.25rem; }
	.field { display: flex; flex-direction: column; gap: 0.4rem; }
	.field label { font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: var(--text-secondary); }
	.field-value { font-size: 0.95rem; color: var(--text-primary); margin: 0; padding: 0.6rem 0; border-bottom: 1px solid var(--border); }
	.field input, .field textarea { background: var(--bg-body); border: 1px solid var(--border); border-radius: var(--radius-sm); padding: 0.6rem 0.75rem; font-size: 0.95rem; color: var(--text-primary); font-family: inherit; width: 100%; box-sizing: border-box; transition: border-color 0.15s; }
	.field input:focus, .field textarea:focus { outline: none; border-color: var(--accent); }
	.field textarea { resize: vertical; }

	/* Buttons */
	.btn-edit { background: none; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.4rem 1rem; border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer; transition: border-color 0.15s, color 0.15s; }
	.btn-edit:hover { border-color: var(--accent); color: var(--accent); }
	.form-actions { display: flex; gap: 0.75rem; justify-content: flex-end; padding-top: 0.5rem; border-top: 1px solid var(--border); }
	.btn-cancel { background: none; border: 1px solid var(--border); color: var(--text-secondary); padding: 0.5rem 1.25rem; border-radius: var(--radius-sm); font-size: 0.875rem; cursor: pointer; }
	.btn-save { background: var(--accent); color: #fff; border: none; padding: 0.5rem 1.5rem; border-radius: var(--radius-sm); font-weight: 600; font-size: 0.875rem; cursor: pointer; transition: opacity 0.15s; }
	.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
	.btn-save:not(:disabled):hover { opacity: 0.85; }
</style>