import i18n from "i18next";
import { initReactI18next } from "react-i18next";
import en from "../../../locales/en.json";
import hi from "../../../locales/hi.json";


export const LANGUAGE_STORAGE_KEY = "eduflow_language";
export const DEFAULT_LANGUAGE = "en";
export const SUPPORTED_LANGUAGES = ["en", "hi"] as const;
export type AppLanguage = (typeof SUPPORTED_LANGUAGES)[number];

const resources = {
  en: { translation: en },
  hi: { translation: hi },
};

const getObjectPathValue = (source: Record<string, unknown>, path: string) => {
  return path.split(".").reduce<unknown>((current, segment) => {
    if (!current || typeof current !== "object") return undefined;
    return (current as Record<string, unknown>)[segment];
  }, source);
};

const stringifyFallback = (value: unknown, key: string) => {
  if (typeof value === "string" && value.trim()) return value;
  return key;
};

const resolveFallbackKey = (key: string) =>
  stringifyFallback(getObjectPathValue(resources.en.translation as Record<string, unknown>, key), key);

export const normalizeLanguage = (value?: string | null): AppLanguage =>
  value?.toLowerCase().startsWith("hi") ? "hi" : "en";

export const getStoredLanguage = (): AppLanguage => {
  if (typeof window === "undefined") return DEFAULT_LANGUAGE;
  const storage = window.localStorage as { getItem?: (key: string) => string | null } | undefined;
  if (!storage || typeof storage.getItem !== "function") return DEFAULT_LANGUAGE;
  return normalizeLanguage(storage.getItem(LANGUAGE_STORAGE_KEY));
};

export const getTranslationResource = (language: AppLanguage) =>
  resources[language].translation as Record<string, unknown>;

const getRawMap = (language: AppLanguage) =>
  ((getTranslationResource(language).raw ?? {}) as Record<string, string>);

export const translateLooseText = (text: string, language: AppLanguage) => {
  if (!text.trim()) return text;
  if (language === "en") return text;

  const rawMap = getRawMap(language);
  if (rawMap[text]) return rawMap[text];

  return text;
};

void i18n.use(initReactI18next).init({
  resources,
  lng: getStoredLanguage(),
  fallbackLng: "en",
  returnNull: false,
  returnEmptyString: false,
  returnObjects: false,
  parseMissingKeyHandler: (key) => {
    console.warn(`[i18n] Missing translation for key: ${key}`);
    return resolveFallbackKey(key);
  },
  missingKeyHandler: (_lng, _ns, key) => {
    console.warn(`[i18n] Missing translation for key: ${key}`);
  },
  returnedObjectHandler: (key) => {
    console.warn(`[i18n] Translation key resolved to a non-string value: ${key}`);
    return resolveFallbackKey(key);
  },
  interpolation: {
    escapeValue: false,
  },
});

const originalTranslate = i18n.t.bind(i18n);

i18n.t = ((key, options) => {
  const fallbackKey = typeof key === "string" ? key : Array.isArray(key) ? key[0] : String(key);

  try {
    const result = originalTranslate(key as never, options as never);
    if (typeof result === "string" && result.trim()) {
      return result;
    }
    return resolveFallbackKey(fallbackKey);
  } catch (error) {
    console.error("[i18n] Translation lookup failed", { key: fallbackKey, error });
    return resolveFallbackKey(fallbackKey);
  }
}) as typeof i18n.t;

if (typeof window !== "undefined") {
  const language = getStoredLanguage();
  document.documentElement.lang = language;
  document.documentElement.dir = "ltr";
}

export const setAppLanguage = async (language: AppLanguage) => {
  if (typeof window !== "undefined") {
    const storage = window.localStorage as { setItem?: (key: string, value: string) => void } | undefined;
    if (storage && typeof storage.setItem === "function") {
      storage.setItem(LANGUAGE_STORAGE_KEY, language);
    }
    document.documentElement.lang = language;
    document.documentElement.dir = "ltr";
  }
  await i18n.changeLanguage(language);
};

export default i18n;
