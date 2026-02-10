export type Locale = 'ro' | 'en';

export interface TranslationKey {
  key: string;
  defaultValue?: string;
}

export interface I18nConfig {
  defaultLocale: Locale;
  supportedLocales: Locale[];
}