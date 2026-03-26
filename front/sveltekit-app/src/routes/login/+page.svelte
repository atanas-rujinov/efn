<script lang="ts">
	import { goto } from '$app/navigation';
	import { authApi } from '$lib/api/auth';
	import type { Role } from '$lib/api/auth';
	import { auth } from '$lib/stores/auth';
	import { notifications } from '$lib/stores/notifications';
	import { ApiError } from '$lib/api/client';

	let role: Role = 'disabled';
	let email = '';
	let password = '';
	let showPassword = false;
	let loading = false;

	async function handleLogin() {
		if (!email || !password) {
			notifications.error('Please fill in all fields.');
			return;
		}
		loading = true;
		try {
			const res = await authApi.login({ email, password, role });
			auth.setToken(res.access_token);
			notifications.success('Welcome back!');
			goto('/dashboard');
		} catch (e) {
			if (e instanceof ApiError) notifications.error(e.detail);
			else notifications.error('Unable to connect. Check your network.');
		} finally {
			loading = false;
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') handleLogin();
	}
</script>

<svelte:head><title>Sign in — Fleet</title></svelte:head>

<div class="shell">
	<aside class="brand">
		<div class="brand__inner">
			<div class="logo">
				<span class="logo__mark">▲</span>
				<span class="logo__name">Fleet</span>
			</div>
			<h1>Welcome back.</h1>
			<p>Sign in to your account to continue.</p>
		</div>
	</aside>

	<main class="form-container">
		<div class="form-card">
			<div class="mobile-header">
				<span class="logo__mark">▲</span>
				<h2>Sign in</h2>
			</div>

			<div class="input-wrap">
				<label for="email">Email</label>
				<input
					id="email"
					type="email"
					bind:value={email}
					on:keydown={handleKeydown}
					placeholder="name@example.com"
					disabled={loading}
					autocomplete="email"
				/>
			</div>

			<div class="input-wrap">
				<div class="pwd-labels">
					<label for="password">Password</label>
					<a href="/forgot" class="forgot-link">Forgot?</a>
				</div>
				<div style="position: relative; display: flex; align-items: center;">
					<input
						id="password"
						type={showPassword ? 'text' : 'password'}
						value={password}
						on:input={(e) => password = e.currentTarget.value}
						on:keydown={handleKeydown}
						placeholder="••••••••"
						disabled={loading}
						autocomplete="current-password"
					/>
					<button
						type="button"
						class="eye-btn"
						on:click={() => showPassword = !showPassword}
						aria-label={showPassword ? 'Hide password' : 'Show password'}
					>
						{#if showPassword}
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></svg>
						{:else}
							<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
						{/if}
					</button>
				</div>
			</div>

			<button class="btn-primary" on:click={handleLogin} disabled={loading}>
				{#if loading}
					<span class="spinner"></span> Logging in...
				{:else}
					Sign in
				{/if}
			</button>

			<p class="signup-prompt">
				Don't have an account? <a href="/signup">Sign up</a>
			</p>
		</div>
	</main>
</div>

<style>
	/* ── Layout ── */
	.shell { display: flex; min-height: 100vh; background: var(--bg-body); }
	
	.brand {
		display: none; width: 40%; background: var(--bg-card);
		border-right: 1px solid var(--border); padding: 3rem;
	}
	@media (min-width: 768px) { .brand { display: flex; flex-direction: column; } }
	
	.brand__inner { max-width: 400px; }
	.logo { display: flex; align-items: center; gap: 0.5rem; margin-bottom: 4rem; }
	.logo__mark { color: var(--accent); font-size: 1.5rem; }
	.logo__name {
		font-family: var(--font-display); font-weight: 700;
		letter-spacing: 0.08em; text-transform: uppercase; font-size: 1.25rem;
	}
	
	.brand h1 {
		font-family: var(--font-display); font-size: 3rem; line-height: 1.1;
		font-weight: 700; margin-bottom: 1rem;
	}
	.brand p { color: var(--text-secondary); font-size: 1.125rem; }

	.form-container { flex: 1; display: flex; align-items: center; justify-content: center; padding: 2rem; }
	.form-card { width: 100%; max-width: 380px; display: flex; flex-direction: column; gap: 1.5rem; }

	.mobile-header { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 1rem; }
	@media (min-width: 768px) { .mobile-header { display: none; } }
	.mobile-header h2 { font-family: var(--font-display); font-size: 2rem; font-weight: 700; }

	/* ── Inputs ── */
	.input-wrap { display: flex; flex-direction: column; gap: 0.5rem; }
	.pwd-labels { display: flex; justify-content: space-between; align-items: center; }
	
	label { font-size: 0.875rem; font-weight: 500; color: var(--text-primary); }
	.forgot-link { font-size: 0.75rem; color: var(--text-secondary); text-decoration: none; }
	.forgot-link:hover { color: var(--text-primary); text-decoration: underline; }

	.input-wrap input {
		width: 100%; padding: 0.75rem 1rem;
		background: var(--bg-body); border: 1px solid var(--border);
		border-radius: var(--radius-sm); color: var(--text-primary);
		font-family: inherit; font-size: 1rem; transition: border-color 0.2s, box-shadow 0.2s;
	}
	.input-wrap input:focus {
		outline: none; border-color: var(--accent);
		box-shadow: 0 0 0 3px var(--accent-dim);
	}
	.input-wrap input:disabled { opacity: 0.5; cursor: not-allowed; }
	.eye-btn {
		position: absolute; right: 0.875rem;
		background: none; border: none;
		color: var(--text-muted); display: flex; align-items: center;
		padding: 0.25rem; cursor: pointer; transition: color 0.2s;
	}
	.eye-btn:hover { color: var(--text-secondary); }

	/* ── Button ── */
	.btn-primary {
		display: flex; align-items: center; justify-content: center; gap: 0.5rem;
		width: 100%; padding: 0.875rem;
		background: var(--accent); color: #080a0f;
		font-family: var(--font-display); font-size: 0.9375rem;
		font-weight: 700; letter-spacing: 0.02em;
		border: none; border-radius: var(--radius-sm);
		cursor: pointer; margin-top: 0.25rem;
		transition: background 0.2s, transform 0.2s, box-shadow 0.2s;
	}
	.btn-primary:hover:not(:disabled) {
		background: var(--accent-hover); transform: translateY(-1px);
		box-shadow: 0 4px 20px rgba(232,255,71,0.25);
	}
	.btn-primary:active:not(:disabled) { transform: translateY(0); }
	.btn-primary:disabled { opacity: 0.7; cursor: not-allowed; }

	.spinner {
		width: 1rem; height: 1rem;
		border: 2px solid rgba(8,10,15,0.2);
		border-top-color: #080a0f; border-radius: 50%;
		animation: spin 0.8s linear infinite;
	}
	@keyframes spin { to { transform: rotate(360deg); } }

	.signup-prompt { text-align: center; font-size: 0.875rem; color: var(--text-secondary); margin-top: 1rem; }
	.signup-prompt a { color: var(--text-primary); font-weight: 500; text-decoration: none; }
	.signup-prompt a:hover { text-decoration: underline; }
</style>