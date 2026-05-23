import { useQuery } from "@tanstack/react-query";
import { useParams } from "react-router-dom";
import { BookOpen, CheckCircle2, Award, TrendingUp, Clock, User, Briefcase, GraduationCap } from "lucide-react";
import VCard from "@/components/ui-custom/VCard";
import VBadge from "@/components/ui-custom/VBadge";
import { getPublicStudentProfile, resolveBackendMediaUrl } from "@/services/api";

/**
 * PublicStudentProfile Component
 * 
 * A public-facing page that allows parents to view student information,
 * enrolled workshops, completed assessments, and academic statistics
 * without requiring authentication.
 */
const PublicStudentProfile = () => {
    const { studentId } = useParams<{ studentId: string }>();

    const { data: profile, isLoading, error } = useQuery({
        queryKey: ["publicStudentProfile", studentId],
        queryFn: () => getPublicStudentProfile(studentId || ""),
        enabled: !!studentId,
    });

    if (isLoading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background">
                <div className="flex flex-col items-center gap-4">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
                    <p className="text-sm text-muted-foreground animate-pulse">Loading Academic Profile...</p>
                </div>
            </div>
        );
    }

    if (error || !profile) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-background p-4">
                <VCard className="p-8 text-center max-w-sm mx-auto border-destructive/20 shadow-xl">
                    <div className="mx-auto w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mb-4">
                        <User className="h-6 w-6 text-destructive" />
                    </div>
                    <h2 className="text-xl font-bold text-foreground mb-2">Profile Not Found</h2>
                    <p className="text-sm text-muted-foreground mb-6">
                        The student profile you are looking for does not exist or is not set to public.
                    </p>
                    <a href="/" className="inline-block px-4 py-2 bg-primary text-primary-foreground rounded-lg transition-transform hover:scale-105 active:scale-95">
                        Return Home
                    </a>
                </VCard>
            </div>
        );
    }

    const { student, stats, active_enrollments, completed_enrollments, submissions } = profile;

    return (
        <div className="min-h-screen bg-background py-8 md:py-16 px-4 sm:px-6 lg:px-8">
            <div className="max-w-5xl mx-auto space-y-8">
                {/* Brand Header */}
                <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                        <div className="bg-primary p-1.5 rounded-lg">
                            <GraduationCap className="h-5 w-5 text-primary-foreground" />
                        </div>
                        <span className="text-xl font-bold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent italic">
                            EduFlow
                        </span>
                    </div>
                </div>

                {/* Header Profile Section */}
                <VCard className="p-8 md:p-12 relative overflow-hidden border-none bg-gradient-to-br from-card to-secondary/30 shadow-2xl">
                    <div className="absolute top-0 right-0 h-64 w-64 bg-primary/5 rounded-full -mr-32 -mt-32 blur-3xl"></div>
                    <div className="absolute bottom-0 left-0 h-48 w-48 bg-info/5 rounded-full -ml-24 -mb-24 blur-3xl"></div>
                    
                    <div className="flex flex-col md:flex-row items-center md:items-start gap-8 relative z-10">
                        <div className="relative group">
                            <div className="absolute -inset-1 bg-gradient-to-r from-primary via-info to-success rounded-full blur opacity-20 group-hover:opacity-40 transition duration-1000"></div>
                            <div className="relative h-32 w-32 md:h-40 md:w-40 rounded-full overflow-hidden border-4 border-background bg-muted shadow-2xl">
                                {student.profile_photo ? (
                                    <img 
                                        src={resolveBackendMediaUrl(student.profile_photo)} 
                                        alt={student.name || "Student"} 
                                        className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110"
                                    />
                                ) : (
                                    <div className="h-full w-full flex items-center justify-center bg-gradient-to-tr from-primary/10 to-info/10 text-primary">
                                        <User className="h-16 w-16" />
                                    </div>
                                )}
                            </div>
                        </div>
                        <div className="text-center md:text-left space-y-4 flex-1">
                            <div>
                                <VBadge variant="outline" className="mb-3 px-3 py-0.5 border-primary/20 text-primary font-bold tracking-widest uppercase text-[10px]">
                                    Verified Student
                                </VBadge>
                                <h1 className="text-3xl md:text-5xl font-extrabold text-foreground tracking-tight">
                                    {student.name}
                                </h1>
                            </div>

                            <div className="flex flex-wrap justify-center md:justify-start gap-4">
                                {student.department && (
                                    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent text-accent-foreground text-xs font-semibold">
                                        <Briefcase className="h-3.5 w-3.5" /> {student.department}
                                    </div>
                                )}
                                <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-accent text-accent-foreground text-xs font-semibold">
                                    <Clock className="h-3.5 w-3.5" /> Joined {student.created_at ? new Date(student.created_at).getFullYear() : "N/A"}
                                </div>
                            </div>
                            
                            {student.bio ? (
                                <p className="text-foreground/70 mt-6 max-w-2xl text-sm md:text-base leading-relaxed italic border-l-2 border-primary/30 pl-4 py-1">
                                    "{student.bio}"
                                </p>
                            ) : (
                                <p className="text-muted-foreground mt-4 text-sm">Consistently working towards academic excellence.</p>
                            )}
                        </div>
                    </div>
                </VCard>

                {/* Stats Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
                    <VCard className="p-6 hover:shadow-xl transition-all group overflow-hidden border-t-4 border-t-primary">
                        <div className="flex items-center justify-between">
                            <div className="h-10 w-10 rounded-xl bg-primary/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                                <BookOpen className="h-5 w-5 text-primary" />
                            </div>
                            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">Engagement</span>
                        </div>
                        <div className="mt-4">
                            <p className="text-3xl font-black text-foreground">{stats.total_workshops}</p>
                            <p className="text-xs font-semibold text-muted-foreground uppercase mt-1">Total Enrolled Workshops</p>
                        </div>
                    </VCard>
                    
                    <VCard className="p-6 hover:shadow-xl transition-all group overflow-hidden border-t-4 border-t-success">
                        <div className="flex items-center justify-between">
                            <div className="h-10 w-10 rounded-xl bg-success/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                                <CheckCircle2 className="h-5 w-5 text-success" />
                            </div>
                            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">Completion</span>
                        </div>
                        <div className="mt-4">
                            <p className="text-3xl font-black text-foreground">{stats.completed_workshops}</p>
                            <p className="text-xs font-semibold text-muted-foreground uppercase mt-1">Workshops Successfully Finished</p>
                        </div>
                    </VCard>
                    
                    <VCard className="p-6 hover:shadow-xl transition-all group overflow-hidden border-t-4 border-t-info">
                        <div className="flex items-center justify-between">
                            <div className="h-10 w-10 rounded-xl bg-info/10 flex items-center justify-center group-hover:scale-110 transition-transform">
                                <TrendingUp className="h-5 w-5 text-info" />
                            </div>
                            <span className="text-[10px] uppercase font-bold text-muted-foreground tracking-tighter">Academic Rank</span>
                        </div>
                        <div className="mt-4">
                            <p className="text-3xl font-black text-foreground">{Math.round(stats.completion_rate)}%</p>
                            <p className="text-xs font-semibold text-muted-foreground uppercase mt-1">Overall Percentage Rate</p>
                        </div>
                    </VCard>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* Workshops Section */}
                    <div className="space-y-6">
                        <div className="flex items-center justify-between px-2">
                             <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                                 <Clock className="h-5 w-5 text-primary" /> Learning Journey
                             </h2>
                             <span className="text-[10px] bg-secondary px-2 py-0.5 rounded-full font-bold text-muted-foreground uppercase">Workshops</span>
                        </div>
                        
                        <VCard className="p-0 overflow-hidden shadow-lg border-none bg-card/60 backdrop-blur-sm">
                            <div className="divide-y divide-border/50">
                                {active_enrollments.length === 0 && completed_enrollments.length === 0 && (
                                    <div className="p-12 text-center">
                                        <BookOpen className="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
                                        <p className="text-sm text-muted-foreground">No workshop enrollments recorded yet.</p>
                                    </div>
                                )}
                                
                                {active_enrollments.map((en) => (
                                    <div key={en.workshop.id} className="p-6 hover:bg-accent/40 transition-colors flex items-center justify-between group">
                                        <div className="flex-1 min-w-0 pr-4">
                                            <h4 className="font-bold text-foreground truncate group-hover:text-primary transition-colors">{en.workshop.title}</h4>
                                            <div className="flex items-center gap-3 mt-1.5">
                                                <span className="text-[10px] text-muted-foreground font-medium bg-muted px-2 py-0.5 rounded">
                                                    Start: {en.workshop.start_date ? new Date(en.workshop.start_date).toLocaleDateString() : "TBD"}
                                                </span>
                                                <span className="text-[10px] text-muted-foreground font-medium bg-muted px-2 py-0.5 rounded">
                                                    Enrolled: {new Date(en.enrolled_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                        </div>
                                        <VBadge variant="default" className="shadow-sm">In Progress</VBadge>
                                    </div>
                                ))}

                                {completed_enrollments.map((en) => (
                                    <div key={en.workshop.id} className="p-6 hover:bg-accent/40 transition-colors flex items-center justify-between group">
                                        <div className="flex-1 min-w-0 pr-4">
                                            <h4 className="font-bold text-foreground truncate group-hover:text-success transition-colors">{en.workshop.title}</h4>
                                            <div className="flex items-center gap-3 mt-1.5 flex-wrap">
                                                <span className="text-[10px] text-muted-foreground font-medium bg-muted px-2 py-0.5 rounded">
                                                    Completed: {new Date(en.enrolled_at).toLocaleDateString()}
                                                </span>
                                                <span className="text-[10px] text-success/70 font-bold uppercase tracking-wider">Verified Result</span>
                                            </div>
                                        </div>
                                        <VBadge variant="success" className="shadow-sm">Completed</VBadge>
                                    </div>
                                ))}
                            </div>
                        </VCard>
                    </div>

                    {/* Assessments Section */}
                    <div className="space-y-6">
                        <div className="flex items-center justify-between px-2">
                             <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                                 <Award className="h-5 w-5 text-primary" /> Performance Report
                             </h2>
                             <span className="text-[10px] bg-secondary px-2 py-0.5 rounded-full font-bold text-muted-foreground uppercase">Assessments</span>
                        </div>

                        <VCard className="p-0 overflow-hidden shadow-lg border-none bg-card/60 backdrop-blur-sm">
                            <div className="divide-y divide-border/50">
                                {submissions.length === 0 && (
                                    <div className="p-12 text-center">
                                        <TrendingUp className="h-10 w-10 text-muted-foreground/30 mx-auto mb-3" />
                                        <p className="text-sm text-muted-foreground">No assessment attempts recorded yet.</p>
                                    </div>
                                )}
                                {submissions.map((sub, idx) => (
                                    <div key={`${sub.assessment.id}-${idx}`} className="p-6 hover:bg-accent/40 transition-colors group">
                                        <div className="flex justify-between items-start mb-4">
                                            <div className="flex-1 min-w-0 pr-2">
                                                <h4 className="font-bold text-foreground truncate group-hover:text-primary transition-colors">{sub.assessment.title}</h4>
                                                <p className="text-[10px] text-muted-foreground mt-1 uppercase font-semibold">Attempt Date: {new Date(sub.submitted_at).toLocaleDateString()}</p>
                                            </div>
                                            <VBadge variant={sub.pass_fail ? "success" : "destructive"} className="shadow-sm">
                                                {sub.pass_fail ? "PASS" : "FAIL"}
                                            </VBadge>
                                        </div>
                                        
                                        <div className="flex items-center gap-4">
                                            <div className="flex-1 h-2.5 bg-secondary rounded-full overflow-hidden shadow-inner">
                                                <div 
                                                    className={`h-full transition-all duration-1000 ease-out shadow-sm ${sub.pass_fail ? 'bg-gradient-to-r from-success to-success/70' : 'bg-gradient-to-r from-destructive to-destructive/70'}`} 
                                                    style={{ width: `${sub.percentage}%` }}
                                                ></div>
                                            </div>
                                            <div className="text-right">
                                                <span className="text-lg font-black text-foreground">{sub.score}</span>
                                                <span className="text-xs text-muted-foreground ml-1">/ {sub.assessment.total_marks}</span>
                                            </div>
                                        </div>
                                        <div className="flex justify-between mt-3 px-1">
                                            <div className="flex items-center gap-1.5">
                                                <span className="h-1.5 w-1.5 rounded-full bg-primary/40"></span>
                                                <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Score: {sub.percentage}%</span>
                                            </div>
                                            <div className="flex items-center gap-1.5">
                                                <span className="h-1.5 w-1.5 rounded-full bg-muted"></span>
                                                <span className="text-[9px] text-muted-foreground uppercase font-bold tracking-wider">Passing: {sub.assessment.pass_mark}</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </VCard>
                    </div>
                </div>

                {/* Footer Brand Verification */}
                <div className="pt-12 text-center border-t border-border mt-12 mb-8">
                    <p className="text-xs text-muted-foreground mb-4">
                        This academic profile is a public verification page generated and secured by EduFlow Learning Management Systems. 
                        Information displayed is synced directly from certified institution records.
                    </p>
                    <div className="flex items-center justify-center gap-6 saturate-0 opacity-40 hover:saturate-100 hover:opacity-100 transition-all duration-500">
                        <div className="flex items-center gap-1.5">
                            <CheckCircle2 className="h-3 w-3 text-success" />
                            <span className="text-[9px] font-bold uppercase tracking-widest">ISO Certified</span>
                        </div>
                        <div className="flex items-center gap-1.5">
                            <Award className="h-3 w-3 text-primary" />
                            <span className="text-[9px] font-bold uppercase tracking-widest">Institution Verified</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PublicStudentProfile;
