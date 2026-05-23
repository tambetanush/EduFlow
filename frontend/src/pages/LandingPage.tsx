import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import {
    GraduationCap,
    BookOpen,
    ClipboardList,
    Award,
    BarChart3,
    Bell,
    Shield,
    Users,
    ArrowRight,
    ChevronRight,
    Star,
    Zap,
    Globe,
    Menu,
    X,
    CheckCircle2,
} from "lucide-react";
import LanguageSwitcher from "@/components/ui-custom/LanguageSwitcher";
import ThemeSwitcher from "@/components/ui-custom/ThemeSwitcher";

const fadeUp = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
        opacity: 1,
        y: 0,
        transition: { delay: i * 0.1, duration: 0.6, ease: "easeOut" as const },
    }),
};

const stagger = {
    visible: { transition: { staggerChildren: 0.08 } },
};

const features = [
    {
        icon: BookOpen,
        title: "Workshop Management",
        description:
            "Create, manage, and track skill development workshops across institutions with real-time monitoring.",
        color: "bg-primary/10 text-primary",
    },
    {
        icon: ClipboardList,
        title: "Smart Assessments",
        description:
            "Design assessments with auto-grading, analytics, and instant feedback for continuous learning.",
        color: "bg-info/10 text-info",
    },
    {
        icon: Award,
        title: "Digital Certificates",
        description:
            "Generate tamper-proof digital certificates with unique verification codes and QR validation.",
        color: "bg-warning/10 text-warning",
    },
    {
        icon: BarChart3,
        title: "Performance Analytics",
        description:
            "Deep insights into student progress, institution performance, and workshop effectiveness.",
        color: "bg-success/10 text-success",
    },
    {
        icon: Shield,
        title: "Role-Based Access",
        description:
            "Granular access control for admins, institutions, educators, and students with secure authentication.",
        color: "bg-destructive/10 text-destructive",
    },
    {
        icon: Bell,
        title: "Smart Notifications",
        description:
            "Stay updated with intelligent alerts for assessments, results, certificates, and announcements.",
        color: "bg-primary/10 text-primary",
    },
];

const stats = [
    { value: "5+", label: "Institutions", icon: Globe },
    { value: "25+", label: "Workshops", icon: BookOpen },
    { value: "150+", label: "Students", icon: Users },
    { value: "98%", label: "Satisfaction", icon: Star },
];

const testimonials = [
    {
        name: "Dr. Priya XYZ",
        role: "Dean, XYZ Delhi",
        text: "EduFlow has transformed how we manage skill development programs. The analytics alone saved us hundreds of hours.",
        avatar: "PS",
    },
    {
        name: "Prof. XYZ Iyer",
        role: "Educator, XYZ Trichy",
        text: "The assessment engine is incredibly powerful. Auto-grading and instant feedback have changed my teaching approach.",
        avatar: "RI",
    },
    {
        name: "Ananya XYZ",
        role: "Student, XYZ Pilani",
        text: "I love how easy it is to track my progress and access materials. The certificates are a great addition to my portfolio.",
        avatar: "AV",
    },
];

const pricingPlans = [
    {
        name: "Starter",
        price: "Free",
        description: "Perfect for individual educators",
        features: [
            "Up to 3 workshops",
            "50 students",
            "Basic assessments",
            "Email support",
        ],
        highlighted: false,
    },
    {
        name: "Professional",
        price: "₹2,999",
        period: "/month",
        description: "For growing institutions",
        features: [
            "Unlimited workshops",
            "500 students",
            "Advanced analytics",
            "Certificate generation",
            "Priority support",
        ],
        highlighted: true,
    },
    {
        name: "Enterprise",
        price: "Custom",
        description: "For large-scale deployments",
        features: [
            "Unlimited everything",
            "Custom branding",
            "API access",
            "Dedicated support",
            "SLA guarantee",
        ],
        highlighted: false,
    },
];

const LandingPage = () => {
    const navigate = useNavigate();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    return (
        <div className="min-h-screen bg-background text-foreground overflow-x-hidden">
            {/* ───── Navbar ───── */}
            <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border/50 bg-background/80 backdrop-blur-xl">
                <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
                    <div className="flex items-center gap-2.5">
                        <div className="flex h-9 w-9 items-center justify-center rounded-xl vidya-gradient shadow-md">
                            <GraduationCap className="h-5 w-5 text-primary-foreground" />
                        </div>
                        <span className="text-xl font-extrabold tracking-tight text-foreground">
                            EduFlow
                        </span>
                    </div>

                    <div className="hidden md:flex items-center gap-8">
                        <a
                            href="#features"
                            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Features
                        </a>
                        <a
                            href="#stats"
                            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Impact
                        </a>
                        <a
                            href="#testimonials"
                            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Testimonials
                        </a>
                        <a
                            href="#pricing"
                            className="text-sm font-medium text-muted-foreground hover:text-foreground transition-colors">
                            Pricing
                        </a>
                        <div className="flex items-center gap-2">
                            <LanguageSwitcher />
                            <ThemeSwitcher />
                        </div>
                    </div>

                    <div className="hidden md:flex items-center gap-3">
                        <button
                            onClick={() => navigate("/login")}
                            className="px-4 py-2 text-sm font-semibold text-foreground hover:text-primary transition-colors">
                            Sign in
                        </button>
                        <button
                            onClick={() => navigate("/signup")}
                            className="inline-flex items-center gap-2 rounded-xl vidya-gradient px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40 transition-all hover:scale-[1.02]">
                            Get Started <ArrowRight className="h-4 w-4" />
                        </button>
                    </div>

                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="md:hidden p-2 rounded-xl hover:bg-accent transition-colors">
                        {mobileMenuOpen ? (
                            <X className="h-5 w-5" />
                        ) : (
                            <Menu className="h-5 w-5" />
                        )}
                    </button>
                </div>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <motion.div
                        initial={{ opacity: 0, height: 0 }}
                        animate={{ opacity: 1, height: "auto" }}
                        exit={{ opacity: 0, height: 0 }}
                        className="md:hidden border-t border-border bg-background">
                        <div className="flex flex-col gap-1 p-4">
                            <a
                                href="#features"
                                onClick={() => setMobileMenuOpen(false)}
                                className="px-3 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground rounded-xl hover:bg-accent transition-all">
                                Features
                            </a>
                            <a
                                href="#stats"
                                onClick={() => setMobileMenuOpen(false)}
                                className="px-3 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground rounded-xl hover:bg-accent transition-all">
                                Impact
                            </a>
                            <a
                                href="#testimonials"
                                onClick={() => setMobileMenuOpen(false)}
                                className="px-3 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground rounded-xl hover:bg-accent transition-all">
                                Testimonials
                            </a>
                            <a
                                href="#pricing"
                                onClick={() => setMobileMenuOpen(false)}
                                className="px-3 py-2.5 text-sm font-medium text-muted-foreground hover:text-foreground rounded-xl hover:bg-accent transition-all">
                                Pricing
                            </a>
                            <div className="flex items-center gap-2 px-1 py-2">
                                <LanguageSwitcher />
                                <ThemeSwitcher />
                            </div>
                            <div className="pt-2 border-t border-border mt-2">
                                <button
                                    onClick={() => navigate("/signup")}
                                    className="w-full rounded-xl vidya-gradient px-5 py-2.5 text-sm font-semibold text-primary-foreground">
                                    Get Started
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </nav>

            {/* ───── Hero ───── */}
            <section className="relative pt-32 pb-20 sm:pt-40 sm:pb-28 px-4">
                {/* Decorative elements */}
                <div className="absolute inset-0 overflow-hidden pointer-events-none">
                    <div className="absolute -top-40 left-1/2 -translate-x-1/2 h-[600px] w-[600px] rounded-full bg-primary/5 blur-[120px]" />
                    <div className="absolute top-20 -left-20 h-72 w-72 rounded-full bg-primary/8 blur-[80px]" />
                    <div className="absolute top-40 -right-20 h-72 w-72 rounded-full bg-info/5 blur-[80px]" />
                </div>

                <div className="relative mx-auto max-w-5xl text-center">
                    <motion.div
                        initial="hidden"
                        animate="visible"
                        variants={stagger}>
                        <motion.div
                            variants={fadeUp}
                            custom={0}
                            className="mb-6">
                            <span className="inline-flex items-center gap-2 rounded-full border border-primary/20 bg-primary/5 px-4 py-1.5 text-xs font-semibold text-primary">
                                <Zap className="h-3.5 w-3.5" />
                                Empowering Education Across India
                            </span>
                        </motion.div>

                        <motion.h1
                            variants={fadeUp}
                            custom={1}
                            className="text-4xl sm:text-5xl lg:text-7xl font-extrabold tracking-tight leading-[1.1]">
                            <span className="text-foreground">Transform</span>{" "}
                            <span className="bg-gradient-to-r from-primary to-[hsl(175,65%,45%)] bg-clip-text text-transparent">
                                Skill Development
                            </span>
                            <br />
                            <span className="text-foreground">
                                with EduFlow
                            </span>
                        </motion.h1>

                        <motion.p
                            variants={fadeUp}
                            custom={2}
                            className="mx-auto mt-6 max-w-2xl text-base sm:text-lg text-muted-foreground leading-relaxed">
                            The all-in-one platform for educational institutions
                            to manage workshops, assessments, certifications,
                            and student performance — beautifully and
                            effortlessly.
                        </motion.p>

                        <motion.div
                            variants={fadeUp}
                            custom={3}
                            className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
                            <button
                                onClick={() => navigate("/signup")}
                                className="group inline-flex items-center gap-2 rounded-2xl vidya-gradient px-8 py-4 text-base font-bold text-primary-foreground shadow-xl shadow-primary/25 hover:shadow-primary/40 transition-all hover:scale-[1.03] active:scale-[0.98]">
                                Start Free Today
                                <ArrowRight className="h-5 w-5 group-hover:translate-x-0.5 transition-transform" />
                            </button>
                            <button
                                onClick={() => navigate("/verify-certificate")}
                                className="inline-flex items-center gap-2 rounded-2xl border border-border bg-card px-8 py-4 text-base font-semibold text-foreground hover:border-primary/30 hover:shadow-lg transition-all">
                                Verify Certificate
                                <ChevronRight className="h-4 w-4 text-muted-foreground" />
                            </button>
                        </motion.div>
                    </motion.div>
                </div>
            </section>

            {/* ───── Stats ───── */}
            <section
                id="stats"
                className="py-16 sm:py-20 px-4 border-t border-border/50">
                <div className="mx-auto max-w-5xl">
                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true, margin: "-50px" }}
                        variants={stagger}
                        className="grid grid-cols-2 lg:grid-cols-4 gap-6">
                        {stats.map(({ value, label, icon: Icon }, i) => (
                            <motion.div
                                key={label}
                                variants={fadeUp}
                                custom={i}
                                className="text-center">
                                <div className="mx-auto mb-3 flex h-12 w-12 items-center justify-center rounded-2xl bg-primary/10">
                                    <Icon className="h-6 w-6 text-primary" />
                                </div>
                                <p className="text-3xl sm:text-4xl font-extrabold text-foreground">
                                    {value}
                                </p>
                                <p className="text-sm text-muted-foreground mt-1">
                                    {label}
                                </p>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* ───── Features ───── */}
            <section id="features" className="py-16 sm:py-24 px-4">
                <div className="mx-auto max-w-6xl">
                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={stagger}
                        className="text-center mb-14">
                        <motion.p
                            variants={fadeUp}
                            custom={0}
                            className="text-sm font-semibold text-primary uppercase tracking-wider mb-3">
                            Everything You Need
                        </motion.p>
                        <motion.h2
                            variants={fadeUp}
                            custom={1}
                            className="text-3xl sm:text-4xl font-extrabold text-foreground">
                            Powerful Features for Modern Education
                        </motion.h2>
                        <motion.p
                            variants={fadeUp}
                            custom={2}
                            className="mx-auto mt-4 max-w-2xl text-muted-foreground">
                            From workshop creation to certificate verification,
                            EduFlow handles the entire lifecycle of skill
                            development programs.
                        </motion.p>
                    </motion.div>

                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true, margin: "-50px" }}
                        variants={stagger}
                        className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                        {features.map(
                            ({ icon: Icon, title, description, color }, i) => (
                                <motion.div
                                    key={title}
                                    variants={fadeUp}
                                    custom={i}
                                    className="group relative rounded-2xl border border-border bg-card p-6 hover:border-primary/20 hover:shadow-xl hover:shadow-primary/5 transition-all duration-300">
                                    <div
                                        className={`mb-4 flex h-12 w-12 items-center justify-center rounded-xl ${color} transition-transform group-hover:scale-110`}>
                                        <Icon className="h-6 w-6" />
                                    </div>
                                    <h3 className="text-lg font-bold text-foreground mb-2">
                                        {title}
                                    </h3>
                                    <p className="text-sm text-muted-foreground leading-relaxed">
                                        {description}
                                    </p>
                                </motion.div>
                            ),
                        )}
                    </motion.div>
                </div>
            </section>

            {/* ───── Testimonials ───── */}
            <section
                id="testimonials"
                className="py-16 sm:py-24 px-4 bg-muted/30">
                <div className="mx-auto max-w-6xl">
                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={stagger}
                        className="text-center mb-14">
                        <motion.p
                            variants={fadeUp}
                            custom={0}
                            className="text-sm font-semibold text-primary uppercase tracking-wider mb-3">
                            Trusted By Educators
                        </motion.p>
                        <motion.h2
                            variants={fadeUp}
                            custom={1}
                            className="text-3xl sm:text-4xl font-extrabold text-foreground">
                            What People Are Saying
                        </motion.h2>
                    </motion.div>

                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true, margin: "-50px" }}
                        variants={stagger}
                        className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {testimonials.map(({ name, role, text, avatar }, i) => (
                            <motion.div
                                key={name}
                                variants={fadeUp}
                                custom={i}
                                className="rounded-2xl border border-border bg-card p-6">
                                <div className="flex gap-1 mb-4">
                                    {[...Array(5)].map((_, j) => (
                                        <Star
                                            key={j}
                                            className="h-4 w-4 fill-warning text-warning"
                                        />
                                    ))}
                                </div>
                                <p className="text-sm text-muted-foreground leading-relaxed mb-6">
                                    "{text}"
                                </p>
                                <div className="flex items-center gap-3">
                                    <div className="flex h-10 w-10 items-center justify-center rounded-full vidya-gradient text-primary-foreground text-sm font-bold">
                                        {avatar}
                                    </div>
                                    <div>
                                        <p className="text-sm font-semibold text-foreground">
                                            {name}
                                        </p>
                                        <p className="text-xs text-muted-foreground">
                                            {role}
                                        </p>
                                    </div>
                                </div>
                            </motion.div>
                        ))}
                    </motion.div>
                </div>
            </section>

            {/* ───── Pricing ───── */}
            <section id="pricing" className="py-16 sm:py-24 px-4">
                <div className="mx-auto max-w-5xl">
                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true }}
                        variants={stagger}
                        className="text-center mb-14">
                        <motion.p
                            variants={fadeUp}
                            custom={0}
                            className="text-sm font-semibold text-primary uppercase tracking-wider mb-3">
                            Simple Pricing
                        </motion.p>
                        <motion.h2
                            variants={fadeUp}
                            custom={1}
                            className="text-3xl sm:text-4xl font-extrabold text-foreground">
                            Choose Your Plan
                        </motion.h2>
                    </motion.div>

                    <motion.div
                        initial="hidden"
                        whileInView="visible"
                        viewport={{ once: true, margin: "-50px" }}
                        variants={stagger}
                        className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
                        {pricingPlans.map(
                            (
                                {
                                    name,
                                    price,
                                    period,
                                    description,
                                    features: planFeatures,
                                    highlighted,
                                },
                                i,
                            ) => (
                                <motion.div
                                    key={name}
                                    variants={fadeUp}
                                    custom={i}
                                    className={`relative rounded-2xl border p-6 sm:p-8 transition-all ${
                                        highlighted
                                            ? "border-primary bg-card shadow-xl shadow-primary/10 scale-[1.02]"
                                            : "border-border bg-card hover:border-primary/20 hover:shadow-lg"
                                    }`}>
                                    {highlighted && (
                                        <span className="absolute -top-3 left-1/2 -translate-x-1/2 rounded-full vidya-gradient px-4 py-1 text-xs font-bold text-primary-foreground">
                                            Most Popular
                                        </span>
                                    )}
                                    <h3 className="text-lg font-bold text-foreground">
                                        {name}
                                    </h3>
                                    <p className="text-sm text-muted-foreground mt-1 mb-4">
                                        {description}
                                    </p>
                                    <div className="flex items-baseline gap-1 mb-6">
                                        <span className="text-4xl font-extrabold text-foreground">
                                            {price}
                                        </span>
                                        {period && (
                                            <span className="text-sm text-muted-foreground">
                                                {period}
                                            </span>
                                        )}
                                    </div>
                                    <ul className="space-y-3 mb-8">
                                        {planFeatures.map((f) => (
                                            <li
                                                key={f}
                                                className="flex items-center gap-2.5 text-sm text-muted-foreground">
                                                <CheckCircle2 className="h-4 w-4 text-primary shrink-0" />
                                                {f}
                                            </li>
                                        ))}
                                    </ul>
                                    <button
                                        onClick={() => navigate("/signup")}
                                        className={`w-full rounded-xl py-3 text-sm font-semibold transition-all ${
                                            highlighted
                                                ? "vidya-gradient text-primary-foreground shadow-lg shadow-primary/25 hover:shadow-primary/40"
                                                : "border border-border bg-card text-foreground hover:border-primary/30 hover:bg-accent"
                                        }`}>
                                        Get Started
                                    </button>
                                </motion.div>
                            ),
                        )}
                    </motion.div>
                </div>
            </section>

            {/* ───── CTA ───── */}
            <section className="py-16 sm:py-24 px-4">
                <motion.div
                    initial={{ opacity: 0, y: 30 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    transition={{ duration: 0.6 }}
                    className="mx-auto max-w-4xl rounded-3xl vidya-gradient p-8 sm:p-14 text-center relative overflow-hidden">
                    <div className="absolute inset-0 bg-[radial-gradient(circle_at_top_right,rgba(255,255,255,0.15),transparent_50%)] pointer-events-none" />
                    <h2 className="relative text-3xl sm:text-4xl font-extrabold text-primary-foreground mb-4">
                        Ready to Transform Your Institution?
                    </h2>
                    <p className="relative text-primary-foreground/80 text-base sm:text-lg max-w-2xl mx-auto mb-8">
                        Join hundreds of institutions already using EduFlow to
                        deliver world-class skill development programs.
                    </p>
                    <button
                        onClick={() => navigate("/signup")}
                        className="relative inline-flex items-center gap-2 rounded-2xl bg-card text-foreground px-8 py-4 text-base font-bold shadow-xl hover:shadow-2xl transition-all hover:scale-[1.03] active:scale-[0.98]">
                        Get Started for Free <ArrowRight className="h-5 w-5" />
                    </button>
                </motion.div>
            </section>

            {/* ───── Footer ───── */}
            <footer className="border-t border-border py-12 px-4">
                <div className="mx-auto max-w-6xl">
                    <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-4 mb-10">
                        <div>
                            <div className="flex items-center gap-2.5 mb-4">
                                <div className="flex h-8 w-8 items-center justify-center rounded-lg vidya-gradient">
                                    <GraduationCap className="h-4 w-4 text-primary-foreground" />
                                </div>
                                <span className="text-lg font-extrabold text-foreground">
                                    EduFlow
                                </span>
                            </div>
                            <p className="text-sm text-muted-foreground leading-relaxed">
                                Bridging the gap between education and skill
                                development across India.
                            </p>
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-foreground mb-3">
                                Platform
                            </h4>
                            <ul className="space-y-2 text-sm text-muted-foreground">
                                <li>
                                    <a
                                        href="#features"
                                        className="hover:text-foreground transition-colors">
                                        Features
                                    </a>
                                </li>
                                <li>
                                    <a
                                        href="#pricing"
                                        className="hover:text-foreground transition-colors">
                                        Pricing
                                    </a>
                                </li>
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        Integrations
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-foreground mb-3">
                                Resources
                            </h4>
                            <ul className="space-y-2 text-sm text-muted-foreground">
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        Documentation
                                    </a>
                                </li>
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        API Reference
                                    </a>
                                </li>
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        Blog
                                    </a>
                                </li>
                            </ul>
                        </div>
                        <div>
                            <h4 className="text-sm font-bold text-foreground mb-3">
                                Company
                            </h4>
                            <ul className="space-y-2 text-sm text-muted-foreground">
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        About
                                    </a>
                                </li>
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        Careers
                                    </a>
                                </li>
                                <li>
                                    <a
                                        href="#"
                                        className="hover:text-foreground transition-colors">
                                        Contact
                                    </a>
                                </li>
                            </ul>
                        </div>
                    </div>
                    <div className="border-t border-border pt-6 flex flex-col sm:flex-row items-center justify-between gap-4">
                        <p className="text-xs text-muted-foreground">
                            © 2026 EduFlow. All rights reserved.
                        </p>
                        <div className="flex gap-6 text-xs text-muted-foreground">
                            <a
                                href="#"
                                className="hover:text-foreground transition-colors">
                                Privacy
                            </a>
                            <a
                                href="#"
                                className="hover:text-foreground transition-colors">
                                Terms
                            </a>
                            <a
                                href="#"
                                className="hover:text-foreground transition-colors">
                                Cookies
                            </a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
