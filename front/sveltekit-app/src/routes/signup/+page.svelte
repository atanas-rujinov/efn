<script lang="ts">
	import { goto } from '$app/navigation';
	import { authApi } from '$lib/api/auth';
	import type { Role } from '$lib/api/auth';
	import { auth } from '$lib/stores/auth';
	import { notifications } from '$lib/stores/notifications';
	import { ApiError } from '$lib/api/client';

	let role: Role = 'disabled';
	let name = '';
	let email = '';
	let password = '';
	let confirmPassword = '';
	let disability = '';
	let showPassword = false;
	let loading = false;

	$: passwordsMatch = !confirmPassword || password === confirmPassword;
	$: strength = getStrength(password);

	function getStrength(pw: string) {
		if (!pw) return { level: 0, label: '', color: '' };
		let s = 0;
		if (pw.length >= 8) s++;
		if (/[A-Z]/.test(pw)) s++;
		if (/[0-9]/.test(pw)) s++;
		if (/[^A-Za-z0-9]/.test(pw)) s++;
		return [
			{ level: 0, label: '', color: '' },
			{ level: 1, label: 'Weak',   color: '#ff4757' },
			{ level: 2, label: 'Fair',   color: '#ffa502' },
			{ level: 3, label: 'Good',   color: '#2ed573' },
			{ level: 4, label: 'Strong', color: '#2ed573' },
		][s];
	}

	function selectRole(r: Role) {
		role = r;
		// reset role-specific fields
		disability = '';
	}

	async function handleSignup() {
		if (!name || !email || !password || !confirmPassword) {
			notifications.error('Please fill in all fields.');
			return;
		}
		if (role === 'disabled' && !disability.trim()) {
			notifications.error('Please describe your disability or condition.');
			return;
		}
		if (!passwordsMatch) {
			notifications.error('Passwords do not match.');
			return;
		}
		if (password.length < 8) {
			notifications.error('Password must be at least 8 characters.');
			return;
		}

		loading = true;
		try {
			const payload =
				role === 'driver'
					? { name, email, password, role: 'driver' as const }
					: { name, email, password, role: 'disabled' as const, disability };

			const res = await authApi.signup(payload);
			auth.setToken(res.access_token);
			notifications.success(
				role === 'driver'
					? "Welcome, driver! Let's get started."
					: 'Account created. Help is on the way!'
			);
			goto('/dashboard');
		} catch (e) {
			if (e instanceof ApiError) notifications.error(e.detail);
			else notifications.error('Unable to connect. Check your network.');
		} finally {
			loading = false;
		}
	}
</script>

<svelte:head><title>Create account — Fleet</title></svelte:head>

<div class="shell">
	<!-- Brand panel -->
	<aside class="brand">
		<div class="brand__inner">
			<div class="logo">
				<span class="logo__mark">▲</span>
				<span class="logo__name">Fleet</span>
			</div>

			<div class="brand__copy">
				{#if role === 'driver'}
					<h1>Help someone<br /><em>today.</em></h1>
					<p>Join our network of volunteer drivers providing transport and errand assistance to people in need.</p>
				{:else}
					<h1>Get the help<br /><em>you deserve.</em></h1>
					<p>Request rides, shopping assistance and more — from vetted volunteer drivers near you.</p>
				{/if}
			</div>

			<div class="checklist">
				{#if role === 'driver'}
					<div class="check"><span class="check__dot" />Set your own availability</div>
					<div class="check"><span class="check__dot" />Accept ride & shop requests</div>
					<div class="check"><span class="check__dot" />Build your driver profile</div>
					<div class="check"><span class="check__dot" />Earn reviews from riders</div>
				{:else}
					<div class="check"><span class="check__dot" />Request rides door-to-door</div>
					<div class="check"><span class="check__dot" />Get shopping done for you</div>
					<div class="check"><span class="check__dot" />Vetted, reviewed drivers</div>
					<div class="check"><span class="check__dot" />Track requests in real-time</div>
				{/if}
			</div>

			<div class="dots" aria-hidden="true">
				{#each Array(64) as _}<div />{/each}
			</div>
		</div>
	</aside>

	<!-- Form panel -->
	<main class="form-panel">
		<div class="form-panel__inner">
			<header>
				<p class="eyebrow">Get started</p>
				<h2 class="title">Create your account</h2>
			</header>

			<!-- Role picker -->
			<div class="role-picker">
				<button
					type="button"
					class="role-btn"
					class:active={role === 'disabled'}
					on:click={() => selectRole('disabled')}
				>
					<span class="role-btn__icon">♿</span>
					<span class="role-btn__label">I need help</span>
					<span class="role-btn__sub">Disabled person</span>
					{#if role === 'disabled'}<span class="role-btn__check">✓</span>{/if}
				</button>
				<button
					type="button"
					class="role-btn"
					class:active={role === 'driver'}
					on:click={() => selectRole('driver')}
				>
					<span class="role-btn__icon">🚗</span>
					<span class="role-btn__label">I want to help</span>
					<span class="role-btn__sub">Volunteer driver</span>
					{#if role === 'driver'}<span class="role-btn__check">✓</span>{/if}
				</button>
			</div>

			<div class="card">
				<!-- Name + Email row -->
				<div class="row-2">
					<div class="field">
						<label for="name">Full name</label>
						<div class="input-wrap">
							<span class="icon">
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
									<circle cx="12" cy="7" r="4"/>
								</svg>
							</span>
							<input id="name" type="text" placeholder="Jane Smith"
								bind:value={name} autocomplete="name" disabled={loading} />
						</div>
					</div>
					<div class="field">
						<label for="email">Email</label>
						<div class="input-wrap">
							<span class="icon">
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
									<polyline points="22,6 12,13 2,6"/>
								</svg>
							</span>
							<input id="email" type="email" placeholder="jane@example.com"
								bind:value={email} autocomplete="email" disabled={loading} />
						</div>
					</div>
				</div>

				<!-- Disability field (disabled role only) -->
				{#if role === 'disabled'}
					<div class="field">
						<label for="disability">
							Disability or condition
							<span class="required">required</span>
						</label>
						<div class="input-wrap">
							<span class="icon">
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<circle cx="12" cy="12" r="10"/>
									<line x1="12" y1="8" x2="12" y2="12"/>
									<line x1="12" y1="16" x2="12.01" y2="16"/>
								</svg>
							</span>
							<input id="disability" type="text"
								placeholder="e.g. visual impairment, mobility difficulty…"
								bind:value={disability} disabled={loading} />
						</div>
						<p class="field-hint">This helps drivers prepare and assist you better.</p>
					</div>
				{/if}

				<!-- Password -->
				<div class="field">
					<label for="password">
						Password
						{#if strength.label}
							<span class="strength-label" style="color:{strength.color}">{strength.label}</span>
						{/if}
					</label>
					<div class="input-wrap">
						<span class="icon">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="3" y="11" width="18" height="11" rx="2"/>
								<path d="M7 11V7a5 5 0 0 1 10 0v4"/>
							</svg>
						</span>
						{#if showPassword}
							<input id="password" type="text" placeholder="Min. 8 characters"
								bind:value={password} autocomplete="new-password" disabled={loading} />
						{:else}
							<input id="password" type="password" placeholder="Min. 8 characters"
								bind:value={password} autocomplete="new-password" disabled={loading} />
						{/if}
						<button type="button" class="eye-btn"
							on:click={() => (showPassword = !showPassword)} aria-label="Toggle password">
							{#if showPassword}
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
									<line x1="1" y1="1" x2="23" y2="23"/>
								</svg>
							{:else}
								<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
									<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
									<circle cx="12" cy="12" r="3"/>
								</svg>
							{/if}
						</button>
					</div>
					{#if password}
						<div class="strength-bar">
							{#each Array(4) as _, i}
								<div class="strength-bar__seg"
									style={i < strength.level ? `background:${strength.color}` : ''} />
							{/each}
						</div>
					{/if}
				</div>

				<!-- Confirm password -->
				<div class="field">
					<label for="confirm">Confirm password</label>
					<div class="input-wrap">
						<span class="icon">
							<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<polyline points="20 6 9 17 4 12"/>
							</svg>
						</span>
						{#if showPassword}
							<input id="confirm" type="text" placeholder="Repeat password"
								bind:value={confirmPassword} autocomplete="new-password"
								disabled={loading} class:error={!passwordsMatch} />
						{:else}
							<input id="confirm" type="password" placeholder="Repeat password"
								bind:value={confirmPassword} autocomplete="new-password"
								disabled={loading} class:error={!passwordsMatch} />
						{/if}
					</div>
					{#if !passwordsMatch}<p class="field-error">Passwords don't match</p>{/if}
				</div>

				<button class="btn-primary" on:click={handleSignup}
					disabled={loading || !passwordsMatch}>
					{#if loading}
						<span class="spinner" />Creating account…
					{:else}
						{role === 'driver' ? 'Join as a driver' : 'Create my account'}
						<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
							<line x1="5" y1="12" x2="19" y2="12"/>
							<polyline points="12 5 19 12 12 19"/>
						</svg>
					{/if}
				</button>
			</div>

			<p class="switch">Already have an account? <a href="/login">Sign in →</a></p>
		</div>
	</main>
</div>

<style>
	.shell {
		display: grid;
		grid-template-columns: 1fr 1fr;
		min-height: 100vh;
	}
	@media (max-width: 860px) {
		.shell { grid-template-columns: 1fr; }
		.brand { display: none; }
	}

	/* ── Brand ── */
	.brand {
		background: var(--bg-elevated);
		border-right: 1px solid var(--border);
		position: relative; overflow: hidden;
	}
	.brand__inner {
		display: flex; flex-direction: column;
		height: 100%; padding: 3rem;
		position: relative; z-index: 1;
	}
	.logo { display: flex; align-items: center; gap: 0.5rem; margin-bottom: auto; }
	.logo__mark { color: var(--accent); font-size: 1.25rem; }
	.logo__name {
		font-family: var(--font-display); font-size: 1.25rem;
		font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
	}
	.brand__copy { margin-bottom: 2rem; }
	.brand__copy h1 {
		font-family: var(--font-display);
		font-size: clamp(2.5rem, 4vw, 3.5rem);
		font-weight: 800; line-height: 1.1;
		letter-spacing: -0.02em; margin-bottom: 1rem;
		transition: opacity 0.3s;
	}
	.brand__copy h1 em { font-style: normal; color: var(--accent); }
	.brand__copy p { color: var(--text-secondary); max-width: 30ch; line-height: 1.7; }

	.checklist { display: flex; flex-direction: column; gap: 0.75rem; }
	.check {
		display: flex; align-items: center; gap: 0.75rem;
		font-size: 0.9rem; color: var(--text-secondary);
	}
	.check__dot {
		width: 7px; height: 7px;
		background: var(--accent); border-radius: 50%; flex-shrink: 0;
	}

	.dots {
		position: absolute; bottom: -1rem; right: -1rem;
		display: grid; grid-template-columns: repeat(8, 1fr);
		gap: 10px; opacity: 0.2;
	}
	.dots div { width: 3px; height: 3px; background: var(--accent); border-radius: 50%; }

	/* ── Form Panel ── */
	.form-panel {
		display: flex; align-items: center;
		justify-content: center; padding: 2rem;
		overflow-y: auto;
	}
	.form-panel__inner { width: 100%; max-width: 460px; }

	.eyebrow {
		font-size: 0.8rem; text-transform: uppercase;
		letter-spacing: 0.1em; color: var(--accent);
		font-weight: 600; margin-bottom: 0.4rem;
	}
	.title {
		font-family: var(--font-display);
		font-size: 2rem; font-weight: 700;
		letter-spacing: -0.02em; margin-bottom: 1.75rem;
	}

	/* ── Role Picker ── */
	.role-picker {
		display: grid; grid-template-columns: 1fr 1fr;
		gap: 0.75rem; margin-bottom: 1.25rem;
	}
	.role-btn {
		position: relative;
		display: flex; flex-direction: column; align-items: flex-start;
		gap: 0.2rem; padding: 1rem 1.125rem;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius);
		cursor: pointer; text-align: left;
		transition: border-color 0.2s, background 0.2s, box-shadow 0.2s;
	}
	.role-btn.active {
		border-color: var(--accent);
		background: var(--accent-dim);
		box-shadow: 0 0 0 1px var(--accent);
	}
	.role-btn:not(.active):hover { border-color: var(--border-hover); }
	.role-btn__icon { font-size: 1.5rem; margin-bottom: 0.25rem; }
	.role-btn__label {
		font-size: 0.875rem; font-weight: 600;
		color: var(--text-primary); font-family: var(--font-display);
	}
	.role-btn__sub { font-size: 0.775rem; color: var(--text-secondary); }
	.role-btn__check {
		position: absolute; top: 0.625rem; right: 0.75rem;
		font-size: 0.75rem; font-weight: 700;
		color: var(--accent);
	}

	/* ── Card ── */
	.card {
		background: var(--bg-card);
		border: 1px solid var(--border);
		border-radius: var(--radius-lg);
		padding: 1.75rem;
		display: flex; flex-direction: column; gap: 1.25rem;
		box-shadow: var(--shadow-card);
		margin-bottom: 1.5rem;
	}
	.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
	@media (max-width: 500px) { .row-2 { grid-template-columns: 1fr; } }

	/* ── Fields ── */
	.field { display: flex; flex-direction: column; gap: 0.4rem; }
	.field label {
		font-size: 0.8125rem; font-weight: 500;
		color: var(--text-secondary); letter-spacing: 0.02em;
		display: flex; align-items: center; gap: 0.5rem;
	}
	.required {
		font-size: 0.7rem; text-transform: uppercase;
		letter-spacing: 0.06em; color: var(--accent);
		background: var(--accent-dim); padding: 1px 6px;
		border-radius: 4px;
	}
	.strength-label { font-size: 0.75rem; font-weight: 600; }
	.field-hint { font-size: 0.775rem; color: var(--text-muted); }
	.field-error { font-size: 0.8rem; color: var(--danger); }

	.input-wrap { position: relative; display: flex; align-items: center; }
	.icon {
		position: absolute; left: 0.875rem;
		color: var(--text-muted); display: flex;
		align-items: center; pointer-events: none; transition: color 0.2s;
	}
	.input-wrap:focus-within .icon { color: var(--accent); }
	.input-wrap input {
		width: 100%;
		background: var(--bg-elevated);
		border: 1px solid var(--border);
		border-radius: var(--radius-sm);
		padding: 0.75rem 0.875rem 0.75rem 2.6rem;
		color: var(--text-primary);
		font-size: 0.9375rem;
		outline: none;
		transition: border-color 0.2s, box-shadow 0.2s;
		-webkit-appearance: none;
	}
	.input-wrap input::placeholder { color: var(--text-muted); }
	.input-wrap input:focus {
		border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-dim);
	}
	.input-wrap input:disabled { opacity: 0.5; cursor: not-allowed; }
	.input-wrap input.error {
		border-color: var(--danger);
		box-shadow: 0 0 0 3px rgba(255,71,87,0.12);
	}

	.eye-btn {
		position: absolute; right: 0.875rem;
		background: none; border: none;
		color: var(--text-muted); display: flex;
		align-items: center; padding: 0.25rem;
		cursor: pointer; transition: color 0.2s;
	}
	.eye-btn:hover { color: var(--text-secondary); }

	.strength-bar { display: flex; gap: 4px; }
	.strength-bar__seg {
		flex: 1; height: 3px;
		background: var(--bg-elevated); border-radius: 2px;
		transition: background 0.3s;
	}

	/* ── Button ── */
	.btn-primary {
		display: flex; align-items: center; justify-content: center; gap: 0.5rem;
		width: 100%; padding: 0.875rem;
		background: var(--accent); color: #080a0f;
		font-family: var(--font-display); font-size: 0.9375rem;
		font-weight: 700; letter-spacing: 0.02em;
		border: none; border-radius: var(--radius-sm); cursor: pointer;
		margin-top: 0.25rem;
		transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
	}
	.btn-primary:hover:not(:disabled) {
		background: var(--accent-hover); transform: translateY(-1px);
		box-shadow: 0 4px 20px rgba(232,255,71,0.25);
	}
	.btn-primary:active:not(:disabled) { transform: translateY(0); }
	.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }

	.spinner {
		width: 15px; height: 15px;
		border: 2px solid rgba(8,10,15,0.3); border-top-color: #080a0f;
		border-radius: 50%; animation: spin 0.6s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	.switch { text-align: center; font-size: 0.875rem; color: var(--text-secondary); }
	.switch a { color: var(--accent); font-weight: 500; margin-left: 0.25rem; }
	.switch a:hover { opacity: 0.8; }
</style>
