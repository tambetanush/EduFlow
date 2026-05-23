import { useState, FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { GraduationCap, ArrowRight, ArrowLeft } from "lucide-react";
import { useTranslation } from "react-i18next";
import VButton from "@/components/ui-custom/VButton";
import VInput from "@/components/ui-custom/VInput";
import VSelect from "@/components/ui-custom/VSelect";
import { useVToast } from "@/components/ui-custom/VToast";
import type { UserRole } from "@/mock/mockData";
import { registerUser } from "@/services/api";

const SignUp = () => {
  const { t } = useTranslation();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { showToast } = useVToast();
  const roleOptions = [
    { value: "student", label: t("roles.student") },
    { value: "educator", label: t("roles.educator") },
    { value: "institution_admin", label: t("roles.institution_admin") },
  ];

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    if (!name || !email || !password) {
      showToast("warning", t("auth.errors.missingFieldsTitle"), t("auth.errors.missingFieldsBody"));
      return;
    }
    setIsLoading(true);
    try {
      await registerUser({ name, email, password, role });
      showToast("success", t("auth.errors.accountCreatedTitle"), t("auth.errors.accountCreatedBody"));
      navigate("/login");
    } catch (err: unknown) {
      showToast("destructive", t("auth.errors.registrationFailedTitle"), err instanceof Error ? err.message : t("auth.errors.registrationFailedBody"));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-background">
      {/* Left decorative panel */}
      <div className="hidden lg:flex lg:w-1/2 relative items-center justify-center overflow-hidden">
        <div className="absolute inset-0 vidya-gradient" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.15),transparent_50%)]" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_bottom_left,rgba(255,255,255,0.1),transparent_50%)]" />
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.7 }}
          className="relative z-10 p-12 text-center max-w-lg"
        >
          <div className="mx-auto mb-8 flex h-20 w-20 items-center justify-center rounded-3xl bg-white/15 backdrop-blur-sm border border-white/20 shadow-2xl">
            <GraduationCap className="h-10 w-10 text-primary-foreground" />
          </div>
          <h2 className="text-4xl font-extrabold text-primary-foreground mb-4 leading-tight">
            {t("auth.signup.welcomeTitle")}
          </h2>
          <p className="text-primary-foreground/70 text-lg leading-relaxed">
            {t("auth.signup.welcomeText")}
          </p>
        </motion.div>
      </div>

      {/* Right sign-up form */}
      <div className="flex flex-1 items-center justify-center px-4 sm:px-8 relative">
        <div className="absolute inset-0 overflow-hidden pointer-events-none lg:hidden">
          <div className="absolute -top-40 -right-40 h-96 w-96 rounded-full bg-primary/5 blur-[100px]" />
          <div className="absolute -bottom-40 -left-40 h-96 w-96 rounded-full bg-primary/5 blur-[100px]" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="relative w-full max-w-md"
        >
          <button
            onClick={() => navigate("/")}
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground mb-8 transition-colors"
          >
            <ArrowLeft className="h-4 w-4" /> {t("common.backToHome")}
          </button>

          <div className="lg:hidden flex items-center gap-2.5 mb-8">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl vidya-gradient shadow-md">
              <GraduationCap className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-extrabold text-foreground">{t("common.appName")}</span>
          </div>

          <h1 className="text-3xl font-extrabold text-foreground mb-2">{t("auth.signup.title")}</h1>
          <p className="text-muted-foreground mb-8">{t("auth.signup.subtitle")}</p>

          <form onSubmit={handleSubmit} className="space-y-5">
            <VInput id="name" label={t("auth.fields.name")} placeholder={t("auth.fields.namePlaceholder")} value={name} onChange={(e) => setName(e.target.value)} />
            <VInput id="email" label={t("auth.fields.email")} type="email" placeholder={t("auth.fields.emailPlaceholder")} value={email} onChange={(e) => setEmail(e.target.value)} />
            <VInput id="password" label={t("auth.fields.password")} type="password" placeholder="••••••••" value={password} onChange={(e) => setPassword(e.target.value)} />
            <VSelect id="role" label={t("auth.signup.roleLabel")} options={roleOptions} value={role} onChange={(e) => setRole(e.target.value as UserRole)} />

            <VButton type="submit" isLoading={isLoading} className="w-full" size="lg">
              {t("auth.signup.button")}
              <ArrowRight className="h-4 w-4" />
            </VButton>
          </form>

          <p className="mt-6 text-center text-sm text-muted-foreground">
            {t("auth.signup.loginCta")}{" "}
            <button onClick={() => navigate("/login")} className="text-primary font-semibold hover:underline">
              {t("auth.signup.loginLink")}
            </button>
          </p>
        </motion.div>
      </div>
    </div>
  );
};

export default SignUp;