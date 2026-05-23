import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { normalizeLanguage, translateLooseText } from "./i18n";

type LocalizableElement = HTMLElement & {
  __i18nOriginalPlaceholder?: string;
  __i18nOriginalTitle?: string;
  __i18nOriginalAriaLabel?: string;
};

type LocalizableText = Text & {
  __i18nOriginalText?: string;
};

const shouldSkipNode = (parent: HTMLElement | null) =>
  !parent ||
  ["SCRIPT", "STYLE", "NOSCRIPT"].includes(parent.tagName) ||
  parent.closest("[data-i18n-skip='true']") !== null;

const setTranslatedValue = (current: string, next: string, apply: (value: string) => void) => {
  if (current !== next) {
    apply(next);
  }
};

const localizeDocument = (language: "en" | "hi") => {
  if (typeof document === "undefined" || !document.body) return;

  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const node = walker.currentNode as LocalizableText;
    const parent = node.parentElement;
    if (shouldSkipNode(parent)) continue;
    const original = node.__i18nOriginalText ?? node.nodeValue ?? "";
    node.__i18nOriginalText = original;
    const translated = language === "en" ? original : translateLooseText(original, language);
    setTranslatedValue(node.nodeValue ?? "", translated, (value) => {
      node.nodeValue = value;
    });
  }

  document.querySelectorAll<LocalizableElement>("[placeholder],[title],[aria-label]").forEach((element) => {
    if (element.hasAttribute("placeholder")) {
      element.__i18nOriginalPlaceholder ??= element.getAttribute("placeholder") ?? "";
      const translated =
        language === "en"
          ? element.__i18nOriginalPlaceholder
          : translateLooseText(element.__i18nOriginalPlaceholder, language);
      setTranslatedValue(element.getAttribute("placeholder") ?? "", translated, (value) => {
        element.setAttribute("placeholder", value);
      });
    }

    if (element.hasAttribute("title")) {
      element.__i18nOriginalTitle ??= element.getAttribute("title") ?? "";
      const translated =
        language === "en"
          ? element.__i18nOriginalTitle
          : translateLooseText(element.__i18nOriginalTitle, language);
      setTranslatedValue(element.getAttribute("title") ?? "", translated, (value) => {
        element.setAttribute("title", value);
      });
    }

    if (element.hasAttribute("aria-label")) {
      element.__i18nOriginalAriaLabel ??= element.getAttribute("aria-label") ?? "";
      const translated =
        language === "en"
          ? element.__i18nOriginalAriaLabel
          : translateLooseText(element.__i18nOriginalAriaLabel, language);
      setTranslatedValue(element.getAttribute("aria-label") ?? "", translated, (value) => {
        element.setAttribute("aria-label", value);
      });
    }
  });
};

export const useAutoLocalizeDocument = () => {
  const { i18n } = useTranslation();

  useEffect(() => {
    const language = normalizeLanguage(i18n.language);
    if (typeof document === "undefined" || !document.body) return;

    let frameId: number | null = null;
    let disconnected = false;
    const observer = new MutationObserver(() => {
      scheduleLocalization();
    });

    const observe = () => {
      if (disconnected) return;
      observer.observe(document.body, {
        childList: true,
        subtree: true,
        characterData: true,
        attributes: true,
        attributeFilter: ["placeholder", "title", "aria-label"],
      });
    };

    const runLocalization = () => {
      observer.disconnect();
      localizeDocument(language);
      observe();
    };

    const scheduleLocalization = () => {
      if (frameId !== null) return;
      frameId = window.requestAnimationFrame(() => {
        frameId = null;
        runLocalization();
      });
    };

    runLocalization();

    return () => {
      disconnected = true;
      if (frameId !== null) {
        window.cancelAnimationFrame(frameId);
      }
      observer.disconnect();
    };
  }, [i18n.language]);
};
