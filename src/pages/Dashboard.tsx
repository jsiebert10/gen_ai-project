import React, { useState } from 'react';
import { useApp } from '@/contexts/AppContext';
import { DashboardSidebar, DashboardTab } from '@/components/layout/DashboardSidebar';
import { StatCard } from '@/components/ui/StatCard';
import { HelpButton } from '@/components/ui/HelpButton';
import { ProgramMatch, VisaData, CareerData, TestPrepData, RoadmapData, GanttItem, Milestone} from '@/types';

function getInitials(name: string): string {
  return name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase()).join('');
}

const PROGRAMS_PER_PAGE = 10;

function OverviewPanel({ onNavigate }: { onNavigate: (tab: DashboardTab) => void }) {
  const { dashboardData } = useApp();
  if (!dashboardData) return null;
  const { stats, activity } = dashboardData.overview;

  const statCards = [
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M9 2L2 6.5v4C2 14 5.134 17.165 9 18c3.866-.835 7-4 7-7.5v-4L9 2z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
          <path d="M6 9l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      ),
      value: String(stats.programs_matched),
      label: 'Recommended Programs',
      subtext: `${stats.strong_matches} strong matches`,
      target: 'programs' as DashboardTab,
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <rect x="2" y="2" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.5" />
          <path d="M2 7h14M7 2v14" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      ),
      value: `${stats.course_plan_semesters} semesters`,
      label: 'Course Strategy',
      subtext: 'Optimized plan ready',
      target: 'test_prep' as DashboardTab,
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.5" />
          <path d="M2 9h14M9 2C7 4.5 6 6.5 6 9s1 4.5 3 7M9 2c2 2.5 3 4.5 3 7s-1 4.5-3 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
        </svg>
      ),
      value: `${stats.visa_steps_total} steps`,
      label: 'Visa Roadmap',
      subtext: `${stats.visa_steps_completed} completed`,
      target: 'visa' as DashboardTab,
    },
    {
      icon: (
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M2 14l4-5 3 3 4-6 3 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      ),
      value: `${stats.career_employment_rate}%`,
      label: 'Career Outlook',
      subtext: 'Sponsorship likelihood',
      target: 'career' as DashboardTab,
    },
  ];

  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        {statCards.map((card) => (
          <StatCard
            key={card.label}
            icon={card.icon}
            value={card.value}
            label={card.label}
            subtext={card.subtext}
            onArrowClick={() => onNavigate(card.target)}
          />
        ))}
      </div>
      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-base font-semibold text-gray-900">Recent Activity</h2>
        <div className="flex flex-col divide-y divide-gray-50">
          {activity.map((item) => (
            <div key={item.label} className="flex items-center justify-between py-3.5">
              <div className="flex items-center gap-3">
                <span className="h-1.5 w-1.5 rounded-full bg-gray-400" />
                <span className="text-sm text-gray-700">{item.label}</span>
              </div>
              <span className="text-sm text-gray-400">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function ProgramsPanel() {
  const { dashboardData } = useApp();
  const [page, setPage] = useState(1);
  if (!dashboardData) return null;
  const { query_summary, items } = dashboardData.programs;

  const sorted = [...items].sort((a, b) => b.match_score - a.match_score);
  const totalPages = Math.max(1, Math.ceil(sorted.length / PROGRAMS_PER_PAGE));
  const pageItems = sorted.slice((page - 1) * PROGRAMS_PER_PAGE, page * PROGRAMS_PER_PAGE);

  return (
    <div className="flex flex-col gap-4">
      <p className="text-sm text-gray-500">{query_summary}</p>
      {pageItems.map((p: ProgramMatch, i: number) => (
        <div key={i} className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <div className="flex items-start justify-between gap-4">
            <div>
              <h3 className="font-semibold text-gray-900">{p.university}</h3>
              <p className="text-sm text-gray-500">{p.program} · {p.country}</p>
              <p className="mt-2 text-sm text-gray-600">{p.reason}</p>
            </div>
            <div className="flex flex-col items-end gap-1 shrink-0">
              <span className="rounded-full bg-gray-900 px-3 py-1 text-xs font-semibold text-white">
                {p.match_score}% match
              </span>
              <span className="text-xs text-gray-400">${p.tuition_usd.toLocaleString()}/yr</span>
            </div>
          </div>
        </div>
      ))}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-4">
          {Array.from({ length: totalPages }, (_, i) => i + 1).map((n) => (
            <button
              key={n}
              onClick={() => setPage(n)}
              className={`flex h-8 w-8 items-center justify-center rounded-lg text-sm font-medium transition-colors ${
                n === page ? 'bg-gray-900 text-white' : 'text-gray-500 hover:bg-gray-100'
              }`}
            >
              {n}
            </button>
          ))}
        </div>
      )}
    </div>
  );
}

function VisaPanel() {
  const { dashboardData } = useApp();
  if (!dashboardData) return null;
  const v: VisaData = dashboardData.visa;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-base font-semibold text-gray-900">{v.visa_type}</h2>
          <span className="text-sm text-gray-500">{v.destination_country}</span>
        </div>
        <div className="flex gap-6 text-sm text-gray-600 mb-4">
          <span>Processing: <strong className="text-gray-900">{v.processing_time}</strong></span>
          <span>Fee: <strong className="text-gray-900">${v.application_fee_usd}</strong></span>
        </div>
        {v.warning && (
          <p className="rounded-xl bg-amber-50 border border-amber-100 px-4 py-3 text-sm text-amber-700">
            ⚠ {v.warning}
          </p>
        )}
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h2 className="mb-4 text-base font-semibold text-gray-900">Required Documents</h2>
        <ul className="flex flex-col gap-2">
          {v.required_documents.map((doc, i) => (
            <li key={i} className="flex items-center gap-3 text-sm text-gray-700">
              <span className="flex h-5 w-5 shrink-0 items-center justify-center rounded-full border border-gray-200 text-xs text-gray-400">
                {i + 1}
              </span>
              {doc}
            </li>
          ))}
        </ul>
      </div>

      {v.tips.length > 0 && (
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-gray-900">Tips</h2>
          <ul className="flex flex-col gap-2">
            {v.tips.map((tip, i) => (
              <li key={i} className="flex items-start gap-3 text-sm text-gray-700">
                <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-gray-400" />
                {tip}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function CareerPanel() {
  const { dashboardData } = useApp();
  if (!dashboardData) return null;
  const c: CareerData = dashboardData.career;

  return (
    <div className="flex flex-col gap-4">
      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between mb-2">
          <h2 className="text-base font-semibold text-gray-900">{c.field} in {c.country}</h2>
          <span className="rounded-full bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
            {c.job_market_outlook}
          </span>
        </div>
        <p className="text-2xl font-semibold text-gray-900 mb-1">
          ${c.average_salary_usd.toLocaleString()}
          <span className="text-sm font-normal text-gray-400">/yr avg</span>
        </p>
        <p className="text-sm text-gray-500">Time to employment: {c.timeline_to_employment}</p>
        {c.insight && (
          <p className="mt-3 border-t border-gray-50 pt-3 text-sm text-gray-600">{c.insight}</p>
        )}
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-gray-900">Top Roles</h3>
          <ul className="flex flex-col gap-2">
            {c.top_roles.map((role, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-gray-400" />{role}
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h3 className="mb-3 text-sm font-semibold text-gray-900">Top Companies</h3>
          <ul className="flex flex-col gap-2">
            {c.top_companies.map((co, i) => (
              <li key={i} className="flex items-center gap-2 text-sm text-gray-700">
                <span className="h-1.5 w-1.5 shrink-0 rounded-full bg-gray-400" />{co}
              </li>
            ))}
          </ul>
        </div>
      </div>

      <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <h3 className="mb-3 text-sm font-semibold text-gray-900">In-Demand Skills</h3>
        <div className="flex flex-wrap gap-2">
          {c.in_demand_skills.map((skill, i) => (
            <span key={i} className="rounded-lg bg-gray-100 px-3 py-1 text-xs font-medium text-gray-700">
              {skill}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function TestPrepPanel() {
  const { dashboardData } = useApp();
  if (!dashboardData) return null;
  const t: TestPrepData = dashboardData.test_prep;

  return (
    <div className="flex flex-col gap-4">
      {t.urgency_flag && (
        <div className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm font-medium text-red-700">
          ⚠ Urgent — application deadline is under 3 months away.
        </div>
      )}

      {t.summary && (
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-2 text-base font-semibold text-gray-900">Summary</h2>
          <p className="text-sm text-gray-600">{t.summary}</p>
        </div>
      )}

      {t.gap_analysis.length > 0 && (
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-gray-900">Score Gap Analysis</h2>
          <div className="flex flex-col gap-3">
            {t.gap_analysis.map((g, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <span className="w-16 font-medium text-gray-900">{g.exam}</span>
                <span className="text-gray-500">Current: {g.current_score ?? '—'}</span>
                <span className="text-gray-500">Target: {g.target_score}</span>
                <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  g.status === 'meets requirement'
                    ? 'bg-green-50 text-green-700'
                    : 'bg-amber-50 text-amber-700'
                }`}>
                  {g.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {t.critical_path.length > 0 && (
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-gray-900">Study Plan</h2>
          <div className="flex flex-col gap-3">
            {t.critical_path.map((step, i) => (
              <div key={i} className="flex items-start gap-4">
                <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-900 text-xs font-semibold text-white">
                  {step.priority}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900">{step.exam} — {step.weeks_needed} weeks</p>
                  <p className="text-xs text-gray-500">{step.reason}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {t.resources.length > 0 && (
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-gray-900">Resources</h2>
          {t.resources.map((r, i) => (
            <div key={i} className="mb-4 last:mb-0">
              <p className="mb-2 text-sm font-semibold text-gray-700">{r.exam}</p>
              <div className="flex flex-col gap-2">
                {r.recommendations.map((rec, j) => (
                  <div key={j} className="flex items-center justify-between text-sm">
                    <a
                      href={rec.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 underline"
                    >
                      {rec.name}
                    </a>
                    <span className="text-xs text-gray-400">{rec.best_for}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const CATEGORY_COLORS: Record<string, string> = {
  test_prep: 'bg-blue-500',
  recommendations: 'bg-green-500',
  application_materials: 'bg-purple-500',
  submission: 'bg-red-500',
  applications: 'bg-orange-500',
};

const URGENCY_STYLES: Record<string, { bg: string; text: string; label: string }> = {
  low:       { bg: 'bg-green-50',  text: 'text-green-700',  label: 'Low — plenty of time' },
  moderate:  { bg: 'bg-blue-50',   text: 'text-blue-700',   label: 'Moderate — stay on track' },
  high:      { bg: 'bg-amber-50',  text: 'text-amber-700',  label: 'High — prioritize now' },
  critical:  { bg: 'bg-red-50',    text: 'text-red-700',    label: 'Critical — urgent action needed' },
  emergency: { bg: 'bg-red-100',   text: 'text-red-800',    label: 'Emergency — consider next cycle' },
};

function GanttChart({ gantt }: { gantt: GanttItem[] }) {
  if (!gantt.length) return null;

  const allDates = gantt.flatMap((g) => [new Date(g.start_date), new Date(g.end_date)]);
  const minDate = new Date(Math.min(...allDates.map((d) => d.getTime())));
  const maxDate = new Date(Math.max(...allDates.map((d) => d.getTime())));
  const totalDays = (maxDate.getTime() - minDate.getTime()) / 86400000 || 1;

  const months: string[] = [];
  const cursor = new Date(minDate.getFullYear(), minDate.getMonth(), 1);
  while (cursor <= maxDate) {
    months.push(cursor.toLocaleString('default', { month: 'short', year: '2-digit' }));
    cursor.setMonth(cursor.getMonth() + 1);
  }

  return (
    <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
      <h2 className="mb-4 text-base font-semibold text-gray-900">Timeline</h2>

      {/* Month headers */}
      <div className="mb-2 flex text-xs text-gray-400" style={{ paddingLeft: '160px' }}>
        {months.map((m) => (
          <div key={m} className="flex-1 text-center">{m}</div>
        ))}
      </div>

      {/* Gantt rows */}
      <div className="flex flex-col gap-2">
        {gantt.map((item, i) => {
          const start = new Date(item.start_date);
          const end = new Date(item.end_date);
          const leftPct = ((start.getTime() - minDate.getTime()) / 86400000 / totalDays) * 100;
          const widthPct = Math.max(((end.getTime() - start.getTime()) / 86400000 / totalDays) * 100, 2);
          const colorClass = CATEGORY_COLORS[item.category] ?? 'bg-gray-400';

          return (
            <div key={i} className="flex items-center gap-3">
              <span className="w-40 shrink-0 truncate text-right text-xs text-gray-600">
                {item.milestone}
              </span>
              <div className="relative flex-1 h-6 rounded bg-gray-50">
                <div
                  className={absolute top-1 h-4 rounded-full ${colorClass} opacity-80}
                  style={{ left: ${leftPct}%, width: ${widthPct}% }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Legend */}
      <div className="mt-4 flex flex-wrap gap-3">
        {Object.entries(CATEGORY_COLORS).map(([cat, color]) => (
          <div key={cat} className="flex items-center gap-1.5">
            <span className={h-2.5 w-2.5 rounded-full ${color}} />
            <span className="text-xs text-gray-500 capitalize">{cat.replace('_', ' ')}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

function RoadmapPanel() {
  const { dashboardData } = useApp();
  const [expanded, setExpanded] = useState<number | null>(null);
  if (!dashboardData?.roadmap) return null;
  const r: RoadmapData = dashboardData.roadmap;
  const urgency = URGENCY_STYLES[r.overview.urgency_level] ?? URGENCY_STYLES.moderate;

  return (
    <div className="flex flex-col gap-4">

      {/* Urgency banner */}
      <div className={rounded-2xl border p-5 ${urgency.bg}}>
        <div className="flex items-start justify-between">
          <div>
            <p className={text-sm font-semibold ${urgency.text}}>{urgency.label}</p>
            <p className={mt-1 text-sm ${urgency.text} opacity-80}>{r.overview.summary}</p>
          </div>
          <div className="text-right shrink-0 ml-4">
            <p className={text-2xl font-bold ${urgency.text}}>{r.overview.days_remaining}</p>
            <p className={text-xs ${urgency.text} opacity-70}>days remaining</p>
          </div>
        </div>
        <div className="mt-3 flex gap-4 text-xs">
          <span className={urgency.text}>
            Deadline: <strong>{r.overview.earliest_deadline}</strong>
          </span>
          <span className={urgency.text}>
            Milestones: <strong>{r.overview.total_milestones}</strong>
          </span>
        </div>
      </div>

      {/* Urgent flags */}
      {r.urgent_flags.length > 0 && r.urgent_flags.map((flag, i) => (
        <div key={i} className="rounded-xl border border-red-100 bg-red-50 px-4 py-3 text-sm text-red-700">
          ⚠ {flag.message}
        </div>
      ))}

      {/* Gantt chart */}
      <GanttChart gantt={r.gantt} />

      {/* Milestones */}
      {r.milestones.length > 0 && (
        <div className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="mb-4 text-base font-semibold text-gray-900">Milestones</h2>
          <div className="flex flex-col gap-3">
            {r.milestones.map((m: Milestone) => (
              <div key={m.id} className="rounded-xl border border-gray-100 overflow-hidden">

                {/* Header */}
                <button
                  onClick={() => setExpanded(expanded === m.id ? null : m.id)}
                  className="flex w-full items-center justify-between px-4 py-3 text-left hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center gap-3">
                    <span className={h-2.5 w-2.5 rounded-full shrink-0 ${CATEGORY_COLORS[m.category] ?? 'bg-gray-400'}} />
                    <span className="text-sm font-medium text-gray-900">{m.title}</span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-xs text-gray-400">
                      {m.start_date} → {m.end_date}
                    </span>
                    {m.weekly_hours && (
                      <span className="rounded-full bg-gray-100 px-2 py-0.5 text-xs text-gray-600">
                        {m.weekly_hours}h/week
                      </span>
                    )}
                    <svg
                      width="14" height="14" viewBox="0 0 14 14" fill="none"
                      className={transition-transform text-gray-400 ${expanded === m.id ? 'rotate-180' : ''}}
                    >
                      <path d="M3 5l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
                    </svg>
                  </div>
                </button>

                {/* Expanded content */}
                {expanded === m.id && (
                  <div className="border-t border-gray-50 px-4 py-4 flex flex-col gap-3">

                    {/* Weekly actions */}
                    {m.weekly_actions.length > 0 && (
                      <div>
                        <p className="mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Weekly Actions</p>
                        <ul className="flex flex-col gap-1.5">
                          {m.weekly_actions.map((action, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-gray-300" />
                              {action}
                            </li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {/* Resources */}
                    {m.resources && m.resources.length > 0 && (
                      <div>
                        <p className="mb-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Resources</p>
                        <div className="flex flex-wrap gap-2">
                          {m.resources.map((res, i) => (
                            
                              key={i}
                              href={res.url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="rounded-lg border border-gray-100 bg-gray-50 px-3 py-1.5 text-xs text-blue-600 hover:bg-gray-100 transition-colors"
                            >
                              {res.name}
                              <span className="ml-1 text-gray-400">({res.type})</span>
                            </a>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Tips */}
                    {m.tips && (
                      <p className="rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">
                        💡 {m.tips}
                      </p>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function Dashboard() {
  const { profile, dashboardData, navigateTo } = useApp();
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');
  const initials = getInitials(profile.fullName || 'User');

  if (!dashboardData) {
    return (
      <div className="flex h-screen items-center justify-center bg-gray-50">
        <div className="text-center">
          <p className="mb-4 text-gray-500">No dashboard data. Please complete the onboarding.</p>
          <button
            onClick={() => navigateTo('step1')}
            className="text-sm font-medium text-gray-900 underline"
          >
            Start over
          </button>
        </div>
      </div>
    );
  }

  const panels: Record<DashboardTab, React.ReactNode> = {
    overview: <OverviewPanel onNavigate={setActiveTab} />,
    programs: <ProgramsPanel />,
    visa: <VisaPanel />,
    career: <CareerPanel />,
    test_prep: <TestPrepPanel />,
    roadmap:   <RoadmapPanel />,
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      <DashboardSidebar activeTab={activeTab} onTabChange={setActiveTab} />
      <div className="flex flex-1 flex-col overflow-auto">
        <header className="flex items-center justify-between border-b border-gray-100 bg-white px-8 py-4">
          <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
          <div
            className="flex h-9 w-9 items-center justify-center rounded-full bg-gray-200 text-sm font-semibold text-gray-600"
            title={profile.fullName}
          >
            {initials}
          </div>
        </header>
        <main className="flex-1 p-8">{panels[activeTab]}</main>
      </div>
      <HelpButton />
    </div>
  );
}
