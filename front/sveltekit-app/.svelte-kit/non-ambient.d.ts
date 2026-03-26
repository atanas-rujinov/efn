
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
		RouteId(): "/(app)" | "/" | "/(app)/dashboard" | "/(app)/helper" | "/(app)/helper/[driverId]" | "/(app)/helper/[driverId]/reviews" | "/login" | "/(app)/requests" | "/(app)/requests/new" | "/reviews" | "/signup";
		RouteParams(): {
			"/(app)/helper/[driverId]": { driverId: string };
			"/(app)/helper/[driverId]/reviews": { driverId: string }
		};
		LayoutParams(): {
			"/(app)": { driverId?: string };
			"/": { driverId?: string };
			"/(app)/dashboard": Record<string, never>;
			"/(app)/helper": { driverId?: string };
			"/(app)/helper/[driverId]": { driverId: string };
			"/(app)/helper/[driverId]/reviews": { driverId: string };
			"/login": Record<string, never>;
			"/(app)/requests": Record<string, never>;
			"/(app)/requests/new": Record<string, never>;
			"/reviews": Record<string, never>;
			"/signup": Record<string, never>
		};
		Pathname(): "/" | "/dashboard" | `/helper/${string}/reviews` & {} | "/login" | "/requests/new" | "/reviews" | "/signup";
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): string & {};
	}
}