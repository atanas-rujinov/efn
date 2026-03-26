
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	type MatcherParam<M> = M extends (param : string) => param is (infer U extends string) ? U : string;

	export interface AppTypes {
		RouteId(): "/(app)" | "/" | "/(app)/dashboard" | "/(app)/drivers" | "/(app)/drivers/[id]" | "/login" | "/(app)/requests" | "/(app)/requests/new" | "/(app)/reviews" | "/(app)/reviews/new" | "/signup";
		RouteParams(): {
			"/(app)/drivers/[id]": { id: string }
		};
		LayoutParams(): {
			"/(app)": { id?: string };
			"/": { id?: string };
			"/(app)/dashboard": Record<string, never>;
			"/(app)/drivers": { id?: string };
			"/(app)/drivers/[id]": { id: string };
			"/login": Record<string, never>;
			"/(app)/requests": Record<string, never>;
			"/(app)/requests/new": Record<string, never>;
			"/(app)/reviews": Record<string, never>;
			"/(app)/reviews/new": Record<string, never>;
			"/signup": Record<string, never>
		};
		Pathname(): "/" | "/dashboard" | `/drivers/${string}` & {} | "/login" | "/requests/new" | "/reviews/new" | "/signup";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}