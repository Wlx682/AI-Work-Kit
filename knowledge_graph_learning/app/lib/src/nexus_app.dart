import 'package:flutter/material.dart';

import '../l10n/app_localizations.dart';
import 'learning_api.dart';
import 'learning_controller.dart';
import 'localization/message_localizer.dart';
import 'models.dart';

const _background = Color(0xFF080B11);
const _surface = Color(0xFF10151E);
const _surfaceHigh = Color(0xFF171E29);
const _cyan = Color(0xFF58F6D6);
const _violet = Color(0xFF9A7CFF);
const _amber = Color(0xFFFFC760);
const _muted = Color(0xFF8B96A8);

class NexusApp extends StatefulWidget {
  const NexusApp({super.key, required this.api, this.initialLocale});

  final LearningApi api;
  final Locale? initialLocale;

  @override
  State<NexusApp> createState() => _NexusAppState();
}

class _NexusAppState extends State<NexusApp> {
  late final LearningController controller = LearningController(widget.api);
  late Locale? locale = widget.initialLocale;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      onGenerateTitle: (context) => AppLocalizations.of(context)!.appTitle,
      locale: locale,
      localizationsDelegates: AppLocalizations.localizationsDelegates,
      supportedLocales: AppLocalizations.supportedLocales,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: _background,
        colorScheme: const ColorScheme.dark(
          primary: _cyan,
          secondary: _violet,
          surface: _surface,
          error: Color(0xFFFF6F7D),
        ),
        fontFamily: 'SF Pro Display',
        textTheme: const TextTheme(
          headlineLarge: TextStyle(
            fontSize: 38,
            fontWeight: FontWeight.w700,
            letterSpacing: -1.3,
          ),
          headlineMedium: TextStyle(
            fontSize: 27,
            fontWeight: FontWeight.w700,
            letterSpacing: -.7,
          ),
          titleLarge: TextStyle(fontSize: 19, fontWeight: FontWeight.w700),
          bodyMedium: TextStyle(
            fontSize: 14,
            height: 1.55,
            color: Color(0xFFC8D0DC),
          ),
        ),
        inputDecorationTheme: InputDecorationTheme(
          filled: true,
          fillColor: const Color(0xFF0B1018),
          hintStyle: const TextStyle(color: Color(0xFF5E697A)),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFF252E3C)),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: Color(0xFF252E3C)),
          ),
          focusedBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(16),
            borderSide: const BorderSide(color: _cyan),
          ),
        ),
      ),
      home: AnimatedBuilder(
        animation: controller,
        builder: (context, _) => _Shell(
          controller: controller,
          locale: locale,
          onLocaleChanged: (value) => setState(() => locale = value),
        ),
      ),
    );
  }
}

class _Shell extends StatelessWidget {
  const _Shell({
    required this.controller,
    required this.locale,
    required this.onLocaleChanged,
  });

  final LearningController controller;
  final Locale? locale;
  final ValueChanged<Locale?> onLocaleChanged;

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        final compact = constraints.maxWidth < 760;
        return Scaffold(
          body: Stack(
            children: [
              const Positioned(
                top: -180,
                right: -120,
                child: _Glow(color: _violet),
              ),
              const Positioned(
                bottom: -220,
                left: 80,
                child: _Glow(color: _cyan),
              ),
              SafeArea(
                child: Row(
                  children: [
                    if (!compact) _SideNavigation(controller: controller),
                    Expanded(
                      child: Column(
                        children: [
                          if (controller.busy)
                            const LinearProgressIndicator(minHeight: 2),
                          if (controller.error != null)
                            _StatusBanner(
                              message: localizeUiMessage(
                                AppLocalizations.of(context)!,
                                controller.error!,
                              ),
                              error: true,
                            )
                          else if (controller.notice != null)
                            _StatusBanner(
                              message: localizeUiMessage(
                                AppLocalizations.of(context)!,
                                controller.notice!,
                              ),
                            ),
                          Expanded(
                            child: controller.course == null
                                ? _GoalWorkspace(controller: controller)
                                : _WorkspaceBody(
                                    controller: controller,
                                    compact: compact,
                                  ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
          bottomNavigationBar: compact && controller.course != null
              ? _MobileNavigation(controller: controller)
              : null,
          floatingActionButton: _LocaleMenu(
            locale: locale,
            onChanged: onLocaleChanged,
          ),
        );
      },
    );
  }
}

class _Glow extends StatelessWidget {
  const _Glow({required this.color});
  final Color color;

  @override
  Widget build(BuildContext context) => Container(
    width: 440,
    height: 440,
    decoration: BoxDecoration(
      shape: BoxShape.circle,
      gradient: RadialGradient(
        colors: [color.withValues(alpha: .09), Colors.transparent],
      ),
    ),
  );
}

class _SideNavigation extends StatelessWidget {
  const _SideNavigation({required this.controller});

  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      width: 252,
      decoration: const BoxDecoration(
        color: Color(0xB20A0E15),
        border: Border(right: BorderSide(color: Color(0xFF1C2430))),
      ),
      padding: const EdgeInsets.fromLTRB(20, 22, 18, 18),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const _Brand(),
          const SizedBox(height: 38),
          _NavItem(
            Icons.hub_outlined,
            localizations.navKnowledgeGraph,
            destination: WorkspaceDestination.graph,
            controller: controller,
          ),
          _NavItem(
            Icons.route_outlined,
            localizations.navLearningPath,
            destination: WorkspaceDestination.path,
            controller: controller,
          ),
          _NavItem(
            Icons.psychology_alt_outlined,
            localizations.navPractice,
            destination: WorkspaceDestination.practice,
            controller: controller,
          ),
          _NavItem(
            Icons.fact_check_outlined,
            localizations.navReview,
            destination: WorkspaceDestination.review,
            controller: controller,
          ),
          _NavItem(
            Icons.query_stats,
            localizations.navProgress,
            destination: WorkspaceDestination.progress,
            controller: controller,
          ),
          const Spacer(),
          Container(
            padding: const EdgeInsets.all(14),
            decoration: BoxDecoration(
              color: _surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF202A38)),
            ),
            child: Row(
              children: [
                const Icon(Icons.hub_outlined, color: _cyan, size: 21),
                const SizedBox(width: 10),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        localizations.currentCourse,
                        style: const TextStyle(
                          fontSize: 9,
                          color: _muted,
                          letterSpacing: 1.2,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        localizations.currentCourseSummary(
                          controller.course?.nodes.length ?? 0,
                          controller.course?.mastery ?? 0,
                        ),
                        style: const TextStyle(fontWeight: FontWeight.w700),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _Brand extends StatelessWidget {
  const _Brand();
  @override
  Widget build(BuildContext context) => const Row(
    children: [
      _BrandMark(),
      SizedBox(width: 11),
      Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'NEXUS',
            style: TextStyle(fontWeight: FontWeight.w900, letterSpacing: 2.4),
          ),
          Text(
            'LEARNING OS',
            style: TextStyle(fontSize: 8, color: _muted, letterSpacing: 2),
          ),
        ],
      ),
    ],
  );
}

class _BrandMark extends StatelessWidget {
  const _BrandMark();
  @override
  Widget build(BuildContext context) => Container(
    width: 36,
    height: 36,
    decoration: BoxDecoration(
      borderRadius: BorderRadius.circular(11),
      gradient: const LinearGradient(
        colors: [_cyan, _violet],
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
      ),
    ),
    child: const Icon(
      Icons.change_history_rounded,
      color: _background,
      size: 22,
    ),
  );
}

class _NavItem extends StatelessWidget {
  const _NavItem(
    this.icon,
    this.label, {
    required this.destination,
    required this.controller,
  });
  final IconData icon;
  final String label;
  final WorkspaceDestination destination;
  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final selected = controller.destination == destination;
    return Padding(
      padding: const EdgeInsets.only(bottom: 7),
      child: Material(
        color: selected ? _cyan.withValues(alpha: .09) : Colors.transparent,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(
            color: selected ? _cyan.withValues(alpha: .16) : Colors.transparent,
          ),
        ),
        child: InkWell(
          key: Key('nav-${destination.name}'),
          onTap: controller.course == null
              ? null
              : () => controller.selectDestination(destination),
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 13, vertical: 12),
            child: Row(
              children: [
                Icon(icon, size: 19, color: selected ? _cyan : _muted),
                const SizedBox(width: 11),
                Expanded(
                  child: Text(
                    label,
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(
                      fontSize: 13,
                      color: selected ? Colors.white : _muted,
                      fontWeight: selected ? FontWeight.w700 : FontWeight.w500,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _MobileNavigation extends StatelessWidget {
  const _MobileNavigation({required this.controller});

  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return NavigationBar(
      key: const Key('mobile-workspace-navigation'),
      height: 64,
      backgroundColor: const Color(0xFF0B1017),
      indicatorColor: _cyan.withValues(alpha: .12),
      selectedIndex: controller.destination.index,
      onDestinationSelected: (index) =>
          controller.selectDestination(WorkspaceDestination.values[index]),
      destinations: [
        NavigationDestination(
          icon: const Icon(Icons.hub_outlined),
          label: localizations.navGraph,
        ),
        NavigationDestination(
          icon: const Icon(Icons.route_outlined),
          label: localizations.navPath,
        ),
        NavigationDestination(
          icon: const Icon(Icons.psychology_alt_outlined),
          label: localizations.navPractice,
        ),
        NavigationDestination(
          icon: const Icon(Icons.fact_check_outlined),
          label: localizations.navReview,
        ),
        NavigationDestination(
          icon: const Icon(Icons.query_stats),
          label: localizations.navProgress,
        ),
      ],
    );
  }
}

class _LocaleMenu extends StatelessWidget {
  const _LocaleMenu({required this.locale, required this.onChanged});

  final Locale? locale;
  final ValueChanged<Locale?> onChanged;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Material(
      color: _surfaceHigh,
      shape: const CircleBorder(),
      elevation: 8,
      child: PopupMenuButton<String>(
        key: const Key('language-menu'),
        tooltip: localizations.language,
        initialValue: locale?.languageCode ?? 'system',
        icon: const Icon(Icons.language_rounded, color: _cyan),
        onSelected: (value) =>
            onChanged(value == 'system' ? null : Locale(value)),
        itemBuilder: (context) => [
          PopupMenuItem(
            value: 'system',
            child: Text(localizations.systemLanguage),
          ),
          PopupMenuItem(
            value: 'zh',
            child: Text(localizations.simplifiedChinese),
          ),
          PopupMenuItem(value: 'en', child: Text(localizations.english)),
        ],
      ),
    );
  }
}

class _StatusBanner extends StatelessWidget {
  const _StatusBanner({required this.message, this.error = false});
  final String message;
  final bool error;

  @override
  Widget build(BuildContext context) => Container(
    width: double.infinity,
    color: (error ? Theme.of(context).colorScheme.error : _cyan).withValues(
      alpha: .1,
    ),
    padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 9),
    child: Row(
      children: [
        Icon(
          error ? Icons.error_outline : Icons.check_circle_outline,
          size: 16,
          color: error ? Theme.of(context).colorScheme.error : _cyan,
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Text(
            message,
            style: TextStyle(
              fontSize: 12,
              color: error ? Theme.of(context).colorScheme.error : _cyan,
            ),
          ),
        ),
      ],
    ),
  );
}

class _GoalWorkspace extends StatefulWidget {
  const _GoalWorkspace({required this.controller});
  final LearningController controller;

  @override
  State<_GoalWorkspace> createState() => _GoalWorkspaceState();
}

class _GoalWorkspaceState extends State<_GoalWorkspace> {
  final goal = TextEditingController();

  @override
  void dispose() {
    goal.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return SingleChildScrollView(
      padding: const EdgeInsets.symmetric(horizontal: 26, vertical: 28),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1040),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _Eyebrow(localizations.personalLearningSpace),
                  const _BrandMark(),
                ],
              ),
              const SizedBox(height: 56),
              Text(
                localizations.goalHeadline,
                style: Theme.of(context).textTheme.headlineLarge,
              ),
              const SizedBox(height: 14),
              Text(
                localizations.goalDescription,
                style: const TextStyle(color: _muted, height: 1.6),
              ),
              const SizedBox(height: 28),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: _surface,
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: const Color(0xFF263140)),
                ),
                child: LayoutBuilder(
                  builder: (context, constraints) {
                    final narrow = constraints.maxWidth < 520;
                    final input = TextField(
                      key: const Key('goal-input'),
                      controller: goal,
                      decoration: InputDecoration(
                        hintText: localizations.goalHint,
                        border: InputBorder.none,
                        enabledBorder: InputBorder.none,
                        focusedBorder: InputBorder.none,
                      ),
                      onSubmitted: (_) =>
                          widget.controller.createGoal(goal.text),
                    );
                    final button = FilledButton.icon(
                      key: const Key('create-goal'),
                      onPressed: widget.controller.busy
                          ? null
                          : () => widget.controller.createGoal(goal.text),
                      style: FilledButton.styleFrom(
                        backgroundColor: _cyan,
                        foregroundColor: _background,
                        padding: const EdgeInsets.symmetric(
                          horizontal: 19,
                          vertical: 17,
                        ),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(14),
                        ),
                      ),
                      icon: const Icon(Icons.auto_awesome, size: 17),
                      label: Text(
                        localizations.generateGraph,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    );
                    if (narrow) {
                      return Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [input, const SizedBox(height: 8), button],
                      );
                    }
                    return Row(
                      children: [
                        Expanded(child: input),
                        button,
                      ],
                    );
                  },
                ),
              ),
              const SizedBox(height: 46),
              _Eyebrow(localizations.learningLoop),
              const SizedBox(height: 15),
              Wrap(
                spacing: 12,
                runSpacing: 12,
                children: [
                  _LoopCard(
                    '01',
                    localizations.loopGoalTitle,
                    localizations.loopGoalDescription,
                    _cyan,
                  ),
                  _LoopCard(
                    '02',
                    localizations.loopEvidenceTitle,
                    localizations.loopEvidenceDescription,
                    _violet,
                  ),
                  _LoopCard(
                    '03',
                    localizations.loopProposalTitle,
                    localizations.loopProposalDescription,
                    _amber,
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LoopCard extends StatelessWidget {
  const _LoopCard(this.number, this.title, this.copy, this.color);
  final String number;
  final String title;
  final String copy;
  final Color color;
  @override
  Widget build(BuildContext context) => Container(
    width: 260,
    padding: const EdgeInsets.all(18),
    decoration: BoxDecoration(
      color: _surface,
      borderRadius: BorderRadius.circular(18),
      border: Border.all(color: const Color(0xFF202A37)),
    ),
    child: Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          number,
          style: TextStyle(
            color: color,
            fontWeight: FontWeight.w800,
            letterSpacing: 1.4,
          ),
        ),
        const SizedBox(height: 22),
        Text(
          title,
          style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 16),
        ),
        const SizedBox(height: 7),
        Text(
          copy,
          style: const TextStyle(color: _muted, fontSize: 12, height: 1.45),
        ),
      ],
    ),
  );
}

class _WorkspaceBody extends StatelessWidget {
  const _WorkspaceBody({required this.controller, required this.compact});

  final LearningController controller;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    switch (controller.destination) {
      case WorkspaceDestination.graph:
        return _GraphWorkspace(controller: controller, compact: compact);
      case WorkspaceDestination.path:
        return _PathView(controller: controller);
      case WorkspaceDestination.practice:
        return _PracticeView(controller: controller);
      case WorkspaceDestination.review:
        return _ReviewView(controller: controller);
      case WorkspaceDestination.progress:
        return _ProgressView(course: controller.course!);
    }
  }
}

class _PathView extends StatelessWidget {
  const _PathView({required this.controller});

  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final recommendation = controller.recommendation;
    if (recommendation == null) {
      return _WorkspacePlaceholder(
        destination: WorkspaceDestination.path,
        icon: Icons.cloud_sync_outlined,
        title: localizations.waitingRecommendation,
        description: localizations.waitingRecommendationDescription,
      );
    }
    final course = controller.course!;
    final nodesById = {for (final node in course.nodes) node.id: node};
    final prerequisites = recommendation.prerequisiteNodeIds
        .map((id) => nodesById[id])
        .whereType<LearningNode>()
        .toList(growable: false);

    return SingleChildScrollView(
      key: const Key('workspace-path'),
      padding: const EdgeInsets.fromLTRB(22, 24, 22, 32),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1060),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 720;
              final header = _PathHeader(course: course, narrow: narrow);
              final recommendationCard = _RecommendationCard(
                recommendation: recommendation,
                onStart: controller.busy
                    ? null
                    : controller.startRecommendedPractice,
              );
              final prerequisitesCard = _PrerequisitesCard(
                prerequisiteNodeIds: recommendation.prerequisiteNodeIds,
                prerequisites: prerequisites,
              );
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  header,
                  const SizedBox(height: 24),
                  if (narrow) ...[
                    recommendationCard,
                    const SizedBox(height: 16),
                    prerequisitesCard,
                  ] else
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(child: recommendationCard),
                        const SizedBox(width: 18),
                        SizedBox(width: 330, child: prerequisitesCard),
                      ],
                    ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _PathHeader extends StatelessWidget {
  const _PathHeader({required this.course, required this.narrow});

  final LearningCourse course;
  final bool narrow;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final title = Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        _Eyebrow(localizations.pathEyebrow),
        const SizedBox(height: 8),
        Text(
          localizations.pathTitle,
          style: Theme.of(context).textTheme.headlineMedium,
        ),
        const SizedBox(height: 7),
        Text(course.title, style: const TextStyle(color: _muted, fontSize: 13)),
      ],
    );
    final mastery = Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: _cyan.withValues(alpha: .07),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _cyan.withValues(alpha: .18)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Icon(Icons.radar, color: _cyan, size: 20),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                localizations.courseMastery,
                style: const TextStyle(
                  color: _muted,
                  fontSize: 8,
                  letterSpacing: 1.2,
                ),
              ),
              Text(
                '${course.mastery}%',
                style: const TextStyle(
                  color: _cyan,
                  fontWeight: FontWeight.w800,
                  fontSize: 18,
                ),
              ),
            ],
          ),
        ],
      ),
    );
    if (narrow) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [title, const SizedBox(height: 16), mastery],
      );
    }
    return Row(
      crossAxisAlignment: CrossAxisAlignment.end,
      children: [
        Expanded(child: title),
        mastery,
      ],
    );
  }
}

class _RecommendationCard extends StatelessWidget {
  const _RecommendationCard({
    required this.recommendation,
    required this.onStart,
  });

  final LearningRecommendation recommendation;
  final Future<void> Function()? onStart;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final node = recommendation.node;
    return Container(
      key: const Key('path-recommendation'),
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: _surface.withValues(alpha: .95),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: _amber.withValues(alpha: .35)),
        boxShadow: [
          BoxShadow(
            color: _amber.withValues(alpha: .06),
            blurRadius: 36,
            spreadRadius: 2,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(
                  horizontal: 10,
                  vertical: 6,
                ),
                decoration: BoxDecoration(
                  color: _amber.withValues(alpha: .1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  localizations.nextNode,
                  style: const TextStyle(
                    color: _amber,
                    fontSize: 9,
                    letterSpacing: 1.4,
                    fontWeight: FontWeight.w800,
                  ),
                ),
              ),
              const Spacer(),
              const Icon(Icons.api_outlined, color: _muted, size: 18),
              const SizedBox(width: 6),
              Text(
                localizations.learningApi,
                style: const TextStyle(color: _muted, fontSize: 10),
              ),
            ],
          ),
          const SizedBox(height: 27),
          Text(node.title, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _PathChip(
                label: localizeMasteryState(localizations, node.masteryState),
                color: _amber,
              ),
              _PathChip(
                label: localizations.progressPercent(node.progress),
                color: _violet,
              ),
              _PathChip(
                label: localizations.prerequisitesCount(
                  recommendation.prerequisiteNodeIds.length,
                ),
                color: _cyan,
              ),
            ],
          ),
          const SizedBox(height: 22),
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              minHeight: 6,
              value: node.progress / 100,
              color: _amber,
              backgroundColor: const Color(0xFF252C37),
            ),
          ),
          const SizedBox(height: 24),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(17),
            decoration: BoxDecoration(
              color: const Color(0xFF0C1119),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF222C39)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  localizations.whyThisNode,
                  style: const TextStyle(
                    color: _muted,
                    fontSize: 9,
                    letterSpacing: 1.4,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  recommendation.reason,
                  style: const TextStyle(height: 1.55),
                ),
              ],
            ),
          ),
          const SizedBox(height: 22),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              key: const Key('start-recommended-practice'),
              onPressed: onStart,
              style: FilledButton.styleFrom(
                backgroundColor: _cyan,
                foregroundColor: _background,
                padding: const EdgeInsets.symmetric(vertical: 17),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              icon: const Icon(Icons.arrow_forward_rounded, size: 18),
              label: Text(
                localizations.startRecommendedPractice,
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PathChip extends StatelessWidget {
  const _PathChip({required this.label, required this.color});
  final String label;
  final Color color;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: .08),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: color.withValues(alpha: .17)),
      ),
      child: Text(
        label.toUpperCase(),
        style: TextStyle(
          color: color,
          fontSize: 9,
          fontWeight: FontWeight.w700,
          letterSpacing: .7,
        ),
      ),
    );
  }
}

class _PrerequisitesCard extends StatelessWidget {
  const _PrerequisitesCard({
    required this.prerequisiteNodeIds,
    required this.prerequisites,
  });

  final List<String> prerequisiteNodeIds;
  final List<LearningNode> prerequisites;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      key: const Key('path-prerequisites'),
      width: double.infinity,
      padding: const EdgeInsets.all(21),
      decoration: BoxDecoration(
        color: _surfaceHigh.withValues(alpha: .88),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFF273140)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.account_tree_outlined, color: _cyan, size: 19),
              const SizedBox(width: 9),
              Text(
                localizations.prerequisites,
                style: const TextStyle(
                  fontWeight: FontWeight.w800,
                  fontSize: 11,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            localizations.prerequisitesDescription,
            style: const TextStyle(color: _muted, fontSize: 11, height: 1.45),
          ),
          const SizedBox(height: 18),
          if (prerequisiteNodeIds.isEmpty)
            Text(
              localizations.noPrerequisites,
              style: const TextStyle(color: _muted),
            )
          else
            for (
              var index = 0;
              index < prerequisiteNodeIds.length;
              index++
            ) ...[
              if (index > 0)
                Container(
                  width: 1,
                  height: 14,
                  margin: const EdgeInsets.only(left: 17),
                  color: _cyan.withValues(alpha: .25),
                ),
              _PrerequisiteTile(
                nodeId: prerequisiteNodeIds[index],
                node: prerequisites
                    .where((node) => node.id == prerequisiteNodeIds[index])
                    .firstOrNull,
              ),
            ],
          const SizedBox(height: 20),
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: _cyan.withValues(alpha: .05),
              borderRadius: BorderRadius.circular(13),
            ),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Icon(Icons.lock_outline, color: _cyan, size: 15),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    localizations.decisionVerbatim,
                    style: const TextStyle(
                      color: _muted,
                      fontSize: 10,
                      height: 1.45,
                    ),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PrerequisiteTile extends StatelessWidget {
  const _PrerequisiteTile({required this.nodeId, required this.node});

  final String nodeId;
  final LearningNode? node;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final value = node;
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: const Color(0xFF0D131C),
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: const Color(0xFF252F3C)),
      ),
      child: Row(
        children: [
          Container(
            width: 34,
            height: 34,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: _cyan.withValues(alpha: .08),
              shape: BoxShape.circle,
              border: Border.all(color: _cyan.withValues(alpha: .25)),
            ),
            child: Text(
              value == null ? '?' : '${value.progress}',
              style: const TextStyle(
                color: _cyan,
                fontSize: 10,
                fontWeight: FontWeight.w800,
              ),
            ),
          ),
          const SizedBox(width: 11),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  value?.title ?? nodeId,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 3),
                Text(
                  value == null
                      ? localizations.apiNode
                      : localizeMasteryState(
                          localizations,
                          value.masteryState,
                        ).toUpperCase(),
                  style: const TextStyle(
                    color: _muted,
                    fontSize: 8,
                    letterSpacing: .8,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _PracticeView extends StatefulWidget {
  const _PracticeView({required this.controller});

  final LearningController controller;

  @override
  State<_PracticeView> createState() => _PracticeViewState();
}

class _PracticeViewState extends State<_PracticeView> {
  final answer = TextEditingController();

  @override
  void dispose() {
    answer.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final node = widget.controller.selectedNode;
    final session = widget.controller.session;
    if (node == null || session == null) {
      return _PracticeEmptyState(controller: widget.controller);
    }
    return SingleChildScrollView(
      key: const Key('workspace-practice'),
      padding: const EdgeInsets.fromLTRB(22, 24, 22, 34),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1020),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 760;
              final brief = _PracticeBrief(
                node: node,
                session: session,
                activity: widget.controller.activity!,
              );
              final evidence = _EvidenceComposer(
                controller: widget.controller,
                answer: answer,
                onChanged: () => setState(() {}),
              );
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _Eyebrow(localizations.practiceEyebrow),
                  const SizedBox(height: 8),
                  Text(
                    localizations.practiceTitle,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    localizations.practiceDescription,
                    style: const TextStyle(color: _muted),
                  ),
                  const SizedBox(height: 24),
                  if (narrow) ...[
                    brief,
                    const SizedBox(height: 16),
                    evidence,
                  ] else
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(flex: 4, child: brief),
                        const SizedBox(width: 18),
                        Expanded(flex: 5, child: evidence),
                      ],
                    ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _PracticeEmptyState extends StatelessWidget {
  const _PracticeEmptyState({required this.controller});

  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Center(
      child: Container(
        key: const Key('workspace-practice'),
        constraints: const BoxConstraints(maxWidth: 520),
        margin: const EdgeInsets.all(24),
        padding: const EdgeInsets.all(30),
        decoration: BoxDecoration(
          color: _surface.withValues(alpha: .92),
          borderRadius: BorderRadius.circular(24),
          border: Border.all(color: const Color(0xFF25303E)),
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.psychology_alt_outlined, color: _cyan, size: 38),
            const SizedBox(height: 18),
            Text(
              localizations.chooseNodeBeforePractice,
              textAlign: TextAlign.center,
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 10),
            Text(
              localizations.practiceRequiresSession,
              textAlign: TextAlign.center,
              style: const TextStyle(color: _muted, height: 1.55),
            ),
            const SizedBox(height: 20),
            OutlinedButton.icon(
              key: const Key('practice-open-path'),
              onPressed: () =>
                  controller.selectDestination(WorkspaceDestination.path),
              icon: const Icon(Icons.route_outlined),
              label: Text(localizations.openLearningPath),
            ),
          ],
        ),
      ),
    );
  }
}

class _PracticeBrief extends StatelessWidget {
  const _PracticeBrief({
    required this.node,
    required this.session,
    required this.activity,
  });

  final LearningNode node;
  final LearningSession session;
  final LearningActivity activity;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      key: const Key('practice-question'),
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _surfaceHigh.withValues(alpha: .9),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _violet.withValues(alpha: .3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                width: 42,
                height: 42,
                decoration: BoxDecoration(
                  color: _violet.withValues(alpha: .1),
                  borderRadius: BorderRadius.circular(13),
                ),
                child: const Icon(
                  Icons.psychology_alt_outlined,
                  color: _violet,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      node.title,
                      style: const TextStyle(
                        fontSize: 17,
                        fontWeight: FontWeight.w800,
                      ),
                    ),
                    Text(
                      '${localizations.progressPercent(node.progress)} · '
                      '${localizeMasteryState(localizations, node.masteryState)}',
                      style: const TextStyle(color: _muted, fontSize: 10),
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: 23),
          Text(
            localizations.practiceQuestion,
            style: const TextStyle(
              color: _muted,
              fontSize: 9,
              letterSpacing: 1.3,
            ),
          ),
          const SizedBox(height: 9),
          Text(
            activity.question,
            style: const TextStyle(fontSize: 16, height: 1.55),
          ),
          const SizedBox(height: 14),
          for (final criterion in activity.rubric)
            Padding(
              padding: const EdgeInsets.only(bottom: 6),
              child: Text(
                '• $criterion',
                style: const TextStyle(color: _muted, fontSize: 12),
              ),
            ),
          const SizedBox(height: 24),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(13),
            decoration: BoxDecoration(
              color: const Color(0xFF0C1119),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Row(
              children: [
                const Icon(Icons.link, color: _cyan, size: 16),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    localizations.sessionLabel(session.id),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                    style: const TextStyle(color: _muted, fontSize: 10),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _EvidenceComposer extends StatelessWidget {
  const _EvidenceComposer({
    required this.controller,
    required this.answer,
    required this.onChanged,
  });

  final LearningController controller;
  final TextEditingController answer;
  final VoidCallback onChanged;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final canSubmit = answer.text.trim().isNotEmpty && !controller.busy;
    return Container(
      key: const Key('practice-evidence-composer'),
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        color: _surface.withValues(alpha: .96),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFF273140)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.edit_note_rounded, color: _cyan, size: 21),
              const SizedBox(width: 9),
              Text(
                localizations.yourEvidence,
                style: const TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w800,
                  letterSpacing: 1.2,
                ),
              ),
            ],
          ),
          const SizedBox(height: 9),
          Text(
            localizations.evidenceDescription,
            style: const TextStyle(color: _muted, fontSize: 11, height: 1.45),
          ),
          const SizedBox(height: 17),
          TextField(
            key: const Key('practice-evidence-input'),
            controller: answer,
            minLines: 7,
            maxLines: 11,
            onChanged: (_) => onChanged(),
            decoration: InputDecoration(
              hintText: localizations.evidenceHint,
              alignLabelWithHint: true,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: Text(
                  localizations.evidenceFlow,
                  style: const TextStyle(color: _muted, fontSize: 10),
                ),
              ),
              Text(
                localizations.characterCount(answer.text.trim().length),
                style: const TextStyle(color: _muted, fontSize: 10),
              ),
            ],
          ),
          const SizedBox(height: 16),
          SizedBox(
            width: double.infinity,
            child: FilledButton.icon(
              key: const Key('practice-submit-evidence'),
              onPressed: canSubmit
                  ? () => controller.submitEvidence(answer.text)
                  : null,
              style: FilledButton.styleFrom(
                backgroundColor: _cyan,
                foregroundColor: _background,
                disabledBackgroundColor: const Color(0xFF27313C),
                padding: const EdgeInsets.symmetric(vertical: 16),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(14),
                ),
              ),
              icon: const Icon(Icons.send_rounded, size: 17),
              label: Text(
                localizations.submitEvidence,
                style: const TextStyle(fontWeight: FontWeight.w800),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ReviewView extends StatelessWidget {
  const _ReviewView({required this.controller});

  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final review = controller.pendingReview;
    if (review == null) {
      return _WorkspacePlaceholder(
        destination: WorkspaceDestination.review,
        icon: Icons.fact_check_outlined,
        title: localizations.noEvalYet,
        description: localizations.noEvalDescription,
      );
    }
    return SingleChildScrollView(
      key: const Key('workspace-review'),
      padding: const EdgeInsets.fromLTRB(22, 24, 22, 34),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1080),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 780;
              final summary = _ReviewSummary(
                controller: controller,
                review: review,
              );
              final timeline = _RuntimeTimeline(events: review.events);
              final title = Text(
                localizations.reviewTitle,
                style: Theme.of(context).textTheme.headlineMedium,
              );
              final status = _ReviewStatus(
                controller: controller,
                review: review,
              );
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _Eyebrow(localizations.reviewEyebrow),
                  const SizedBox(height: 8),
                  if (narrow) ...[
                    title,
                    const SizedBox(height: 12),
                    status,
                  ] else
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Expanded(child: title),
                        status,
                      ],
                    ),
                  const SizedBox(height: 24),
                  if (narrow) ...[
                    summary,
                    const SizedBox(height: 16),
                    timeline,
                  ] else
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Expanded(flex: 5, child: summary),
                        const SizedBox(width: 18),
                        Expanded(flex: 4, child: timeline),
                      ],
                    ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _ReviewStatus extends StatelessWidget {
  const _ReviewStatus({required this.controller, required this.review});

  final LearningController controller;
  final RuntimeReview review;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final decided = controller.reviewOutcome != null;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 11, vertical: 7),
      decoration: BoxDecoration(
        color: (decided ? _cyan : _amber).withValues(alpha: .08),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: (decided ? _cyan : _amber).withValues(alpha: .25),
        ),
      ),
      child: Text(
        localizeRuntimeStatus(
          localizations,
          controller.reviewOutcome ?? review.status,
        ).toUpperCase(),
        style: TextStyle(
          color: decided ? _cyan : _amber,
          fontSize: 9,
          fontWeight: FontWeight.w800,
          letterSpacing: .8,
        ),
      ),
    );
  }
}

class _ReviewSummary extends StatelessWidget {
  const _ReviewSummary({required this.controller, required this.review});

  final LearningController controller;
  final RuntimeReview review;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Column(
      children: [
        if (controller.submittedEvidence != null) ...[
          Container(
            key: const Key('review-evidence'),
            width: double.infinity,
            padding: const EdgeInsets.all(17),
            decoration: BoxDecoration(
              color: _surface,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: const Color(0xFF263140)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  localizations.submittedEvidence,
                  style: const TextStyle(
                    color: _muted,
                    fontSize: 9,
                    letterSpacing: 1.2,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  controller.submittedEvidence!,
                  style: const TextStyle(height: 1.55),
                ),
              ],
            ),
          ),
          const SizedBox(height: 14),
        ],
        _EvaluationCard(review: review),
        if (review.tutorContent.isNotEmpty) ...[
          const SizedBox(height: 14),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: _cyan.withValues(alpha: .05),
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: _cyan.withValues(alpha: .18)),
            ),
            child: Text(
              review.tutorContent,
              style: const TextStyle(color: Color(0xFFBBC8D3), height: 1.5),
            ),
          ),
        ],
        if (review.proposal != null) ...[
          const SizedBox(height: 14),
          _ProposalCard(controller: controller, proposal: review.proposal!),
        ],
      ],
    );
  }
}

class _RuntimeTimeline extends StatelessWidget {
  const _RuntimeTimeline({required this.events});

  final List<RuntimeEvent> events;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      key: const Key('runtime-timeline'),
      width: double.infinity,
      padding: const EdgeInsets.all(19),
      decoration: BoxDecoration(
        color: _surfaceHigh.withValues(alpha: .88),
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: const Color(0xFF273140)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.timeline_rounded, color: _violet, size: 19),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  localizations.runtimeTimeline,
                  style: const TextStyle(
                    fontWeight: FontWeight.w800,
                    fontSize: 11,
                    letterSpacing: 1.1,
                  ),
                ),
              ),
              Text(
                localizations.eventCount(events.length),
                style: const TextStyle(color: _muted, fontSize: 8),
              ),
            ],
          ),
          const SizedBox(height: 17),
          if (events.isEmpty)
            Text(
              localizations.noRuntimeEvents,
              style: const TextStyle(color: _muted),
            )
          else
            for (var index = 0; index < events.length; index++)
              _RuntimeEventTile(
                event: events[index],
                last: index == events.length - 1,
              ),
        ],
      ),
    );
  }
}

class _RuntimeEventTile extends StatelessWidget {
  const _RuntimeEventTile({required this.event, required this.last});

  final RuntimeEvent event;
  final bool last;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final completed = event.status == 'completed';
    final color = completed
        ? _cyan
        : event.status == 'paused'
        ? _amber
        : _violet;
    final payloadKeys = event.payload.keys.take(3).join(' · ');
    return Row(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        SizedBox(
          width: 24,
          child: Column(
            children: [
              Container(
                width: 10,
                height: 10,
                decoration: BoxDecoration(
                  color: color,
                  shape: BoxShape.circle,
                  boxShadow: [
                    BoxShadow(
                      color: color.withValues(alpha: .3),
                      blurRadius: 8,
                    ),
                  ],
                ),
              ),
              if (!last)
                Container(width: 1, height: 48, color: const Color(0xFF354050)),
            ],
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: Padding(
            padding: const EdgeInsets.only(bottom: 13),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    Expanded(
                      child: Text(
                        event.phase.replaceAll('_', ' ').toUpperCase(),
                        key: Key('runtime-event-${event.phase}'),
                        style: const TextStyle(
                          fontSize: 10,
                          fontWeight: FontWeight.w800,
                          letterSpacing: .7,
                        ),
                      ),
                    ),
                    Text(
                      '#${event.sequence} · '
                      '${localizeRuntimeStatus(localizations, event.status)}',
                      style: TextStyle(color: color, fontSize: 8),
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  payloadKeys.isEmpty
                      ? localizations.noPayloadFields
                      : payloadKeys,
                  style: const TextStyle(color: _muted, fontSize: 9),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
}

class _ProgressView extends StatelessWidget {
  const _ProgressView({required this.course});

  final LearningCourse course;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final counts = <String, int>{};
    for (final node in course.nodes) {
      counts.update(node.masteryState, (count) => count + 1, ifAbsent: () => 1);
    }
    final states = counts.keys.toList()..sort();
    return SingleChildScrollView(
      key: const Key('workspace-progress'),
      padding: const EdgeInsets.fromLTRB(22, 24, 22, 34),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 1080),
          child: LayoutBuilder(
            builder: (context, constraints) {
              final narrow = constraints.maxWidth < 700;
              final stateWidth = narrow
                  ? (constraints.maxWidth - 10) / 2
                  : (constraints.maxWidth - 30) / 4;
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _Eyebrow(localizations.progressEyebrow),
                  const SizedBox(height: 8),
                  Text(
                    localizations.progressTitle,
                    style: Theme.of(context).textTheme.headlineMedium,
                  ),
                  const SizedBox(height: 24),
                  _MasteryOverview(course: course),
                  const SizedBox(height: 18),
                  Wrap(
                    spacing: 10,
                    runSpacing: 10,
                    children: [
                      for (final state in states)
                        SizedBox(
                          width: stateWidth,
                          child: _StateCountCard(
                            state: state,
                            count: counts[state]!,
                          ),
                        ),
                    ],
                  ),
                  const SizedBox(height: 20),
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: _surface.withValues(alpha: .94),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: const Color(0xFF263140)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          localizations.nodeProgress,
                          style: const TextStyle(
                            fontSize: 10,
                            fontWeight: FontWeight.w800,
                            letterSpacing: 1.2,
                          ),
                        ),
                        const SizedBox(height: 16),
                        for (
                          var index = 0;
                          index < course.nodes.length;
                          index++
                        ) ...[
                          if (index > 0) const SizedBox(height: 14),
                          _NodeProgressRow(node: course.nodes[index]),
                        ],
                      ],
                    ),
                  ),
                ],
              );
            },
          ),
        ),
      ),
    );
  }
}

class _MasteryOverview extends StatelessWidget {
  const _MasteryOverview({required this.course});

  final LearningCourse course;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      key: const Key('progress-mastery'),
      width: double.infinity,
      padding: const EdgeInsets.all(22),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            _cyan.withValues(alpha: .12),
            _violet.withValues(alpha: .08),
          ],
        ),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: _cyan.withValues(alpha: .22)),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 76,
            height: 76,
            child: Stack(
              alignment: Alignment.center,
              children: [
                CircularProgressIndicator(
                  value: course.mastery / 100,
                  strokeWidth: 7,
                  color: _cyan,
                  backgroundColor: const Color(0xFF283241),
                ),
                Text(
                  '${course.mastery}%',
                  style: const TextStyle(
                    fontWeight: FontWeight.w900,
                    fontSize: 16,
                  ),
                ),
              ],
            ),
          ),
          const SizedBox(width: 18),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  course.title,
                  style: const TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w800,
                  ),
                ),
                const SizedBox(height: 6),
                Text(
                  localizations.nodesCalculatedByApi(course.nodes.length),
                  style: const TextStyle(color: _muted, fontSize: 11),
                ),
              ],
            ),
          ),
          const Icon(Icons.lock_outline, color: _cyan, size: 20),
        ],
      ),
    );
  }
}

Color _stateColor(String state) {
  if (state == 'verified') return _cyan;
  if (state == 'practiced') return _violet;
  if (state == 'recommended') return _amber;
  if (state == 'locked') return const Color(0xFF657286);
  return const Color(0xFF7BC8FF);
}

class _StateCountCard extends StatelessWidget {
  const _StateCountCard({required this.state, required this.count});

  final String state;
  final int count;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final color = _stateColor(state);
    return Container(
      key: Key('progress-state-$state'),
      padding: const EdgeInsets.all(15),
      decoration: BoxDecoration(
        color: color.withValues(alpha: .07),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withValues(alpha: .22)),
      ),
      child: Row(
        children: [
          Text(
            '$count',
            style: TextStyle(
              color: color,
              fontSize: 22,
              fontWeight: FontWeight.w900,
            ),
          ),
          const SizedBox(width: 9),
          Expanded(
            child: Text(
              localizeMasteryState(localizations, state).toUpperCase(),
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(fontSize: 9, letterSpacing: .7),
            ),
          ),
        ],
      ),
    );
  }
}

class _NodeProgressRow extends StatelessWidget {
  const _NodeProgressRow({required this.node});

  final LearningNode node;

  @override
  Widget build(BuildContext context) {
    final color = _stateColor(node.masteryState);
    return Row(
      children: [
        Expanded(
          flex: 3,
          child: Text(
            node.title,
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w700),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          flex: 4,
          child: ClipRRect(
            borderRadius: BorderRadius.circular(5),
            child: LinearProgressIndicator(
              minHeight: 6,
              value: node.progress / 100,
              color: color,
              backgroundColor: const Color(0xFF28313D),
            ),
          ),
        ),
        const SizedBox(width: 10),
        SizedBox(
          width: 34,
          child: Text(
            '${node.progress}%',
            textAlign: TextAlign.end,
            style: TextStyle(color: color, fontSize: 10),
          ),
        ),
      ],
    );
  }
}

class _WorkspacePlaceholder extends StatelessWidget {
  const _WorkspacePlaceholder({
    required this.destination,
    required this.icon,
    required this.title,
    required this.description,
  });

  final WorkspaceDestination destination;
  final IconData icon;
  final String title;
  final String description;

  @override
  Widget build(BuildContext context) => Center(
    child: Container(
      key: Key('workspace-${destination.name}'),
      constraints: const BoxConstraints(maxWidth: 520),
      margin: const EdgeInsets.all(24),
      padding: const EdgeInsets.all(30),
      decoration: BoxDecoration(
        color: _surface.withValues(alpha: .9),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: const Color(0xFF25303E)),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(
            width: 58,
            height: 58,
            decoration: BoxDecoration(
              color: _cyan.withValues(alpha: .08),
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: _cyan.withValues(alpha: .22)),
            ),
            child: Icon(icon, color: _cyan, size: 27),
          ),
          const SizedBox(height: 20),
          Text(title, style: Theme.of(context).textTheme.headlineMedium),
          const SizedBox(height: 10),
          Text(
            description,
            textAlign: TextAlign.center,
            style: const TextStyle(color: _muted, height: 1.55),
          ),
        ],
      ),
    ),
  );
}

class _GraphWorkspace extends StatelessWidget {
  const _GraphWorkspace({required this.controller, required this.compact});
  final LearningController controller;
  final bool compact;

  @override
  Widget build(BuildContext context) {
    final course = controller.course!;
    final graph = _GraphCanvas(controller: controller, course: course);
    final panel = _LearningPanel(controller: controller);
    if (compact) {
      return SingleChildScrollView(
        child: Column(
          children: [
            _GraphHeader(course: course, compact: true),
            SizedBox(height: 540, child: graph),
            panel,
          ],
        ),
      );
    }
    return Column(
      children: [
        _GraphHeader(course: course),
        Expanded(
          child: Row(
            children: [
              Expanded(child: graph),
              SizedBox(width: 410, child: panel),
            ],
          ),
        ),
      ],
    );
  }
}

class _GraphHeader extends StatelessWidget {
  const _GraphHeader({required this.course, this.compact = false});
  final LearningCourse course;
  final bool compact;
  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Padding(
      padding: EdgeInsets.fromLTRB(
        compact ? 18 : 28,
        22,
        compact ? 18 : 28,
        14,
      ),
      child: Row(
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                _Eyebrow(localizations.knowledgeGraphEyebrow),
                const SizedBox(height: 7),
                Text(
                  course.title,
                  maxLines: 1,
                  overflow: TextOverflow.ellipsis,
                  style: Theme.of(context).textTheme.headlineMedium,
                ),
              ],
            ),
          ),
          const SizedBox(width: 18),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text(
                localizations.courseMastery,
                style: const TextStyle(
                  fontSize: 9,
                  letterSpacing: 1.3,
                  color: _muted,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '${course.mastery}%',
                style: const TextStyle(
                  fontSize: 21,
                  fontWeight: FontWeight.w800,
                  color: _cyan,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _GraphLayout {
  const _GraphLayout({required this.positions, required this.edges});

  final Map<String, Offset> positions;
  final List<LearningEdge> edges;
}

class _GraphCanvas extends StatelessWidget {
  const _GraphCanvas({required this.controller, required this.course});
  final LearningController controller;
  final LearningCourse course;

  _GraphLayout _treeLayout() {
    final byId = {for (final node in course.nodes) node.id: node};
    final indexById = {
      for (var index = 0; index < course.nodes.length; index++)
        course.nodes[index].id: index,
    };
    final incoming = {
      for (final node in course.nodes) node.id: <LearningEdge>[],
    };
    final children = {for (final node in course.nodes) node.id: <String>[]};
    for (final edge in course.edges) {
      if (!byId.containsKey(edge.sourceNodeId) ||
          !byId.containsKey(edge.targetNodeId)) {
        continue;
      }
      incoming[edge.targetNodeId]!.add(edge);
    }

    final roots = <String>[];
    final treeEdges = <LearningEdge>[];
    for (final node in course.nodes) {
      final parents = incoming[node.id]!;
      if (parents.isEmpty) {
        roots.add(node.id);
      } else {
        final parent = parents.first;
        treeEdges.add(parent);
        children[parent.sourceNodeId]!.add(node.id);
      }
    }
    if (roots.isEmpty) return _linearLayout(course.nodes);
    roots.sort((left, right) => indexById[left]!.compareTo(indexById[right]!));
    for (final entry in children.entries) {
      entry.value.sort(
        (left, right) => indexById[left]!.compareTo(indexById[right]!),
      );
    }

    final rawPositions = <String, Offset>{};
    final visited = <String>{};
    var nextLeaf = 0.0;
    var maxDepth = 0;

    double place(String nodeId, int depth) {
      if (visited.contains(nodeId)) return rawPositions[nodeId]?.dx ?? nextLeaf;
      visited.add(nodeId);
      if (depth > maxDepth) maxDepth = depth;
      final childIds = children[nodeId]!
          .where((childId) => !visited.contains(childId))
          .toList(growable: false);
      if (childIds.isEmpty) {
        final x = nextLeaf;
        nextLeaf += 1;
        rawPositions[nodeId] = Offset(x, depth.toDouble());
        return x;
      }
      final childXs = childIds
          .map((childId) => place(childId, depth + 1))
          .toList();
      final x = (childXs.first + childXs.last) / 2;
      rawPositions[nodeId] = Offset(x, depth.toDouble());
      return x;
    }

    for (final root in roots) {
      place(root, 0);
    }
    for (final node in course.nodes) {
      if (!visited.contains(node.id)) place(node.id, 0);
    }

    final maxX = nextLeaf <= 1 ? 1.0 : nextLeaf - 1;
    final positions = <String, Offset>{};
    for (final entry in rawPositions.entries) {
      positions[entry.key] = Offset(
        nextLeaf <= 1 ? .5 : entry.value.dx / maxX,
        maxDepth == 0 ? .5 : entry.value.dy / maxDepth,
      );
    }
    return _GraphLayout(positions: positions, edges: treeEdges);
  }

  _GraphLayout _linearLayout(List<LearningNode> ordered) {
    final positions = <String, Offset>{};
    for (var index = 0; index < ordered.length; index++) {
      positions[ordered[index].id] = Offset(
        ordered.length == 1 ? .5 : index / (ordered.length - 1),
        .5,
      );
    }
    return _GraphLayout(positions: positions, edges: const []);
  }

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      key: const Key('graph-canvas'),
      margin: const EdgeInsets.fromLTRB(18, 0, 14, 18),
      decoration: BoxDecoration(
        color: const Color(0xB20A0F16),
        borderRadius: BorderRadius.circular(22),
        border: Border.all(color: const Color(0xFF202A37)),
      ),
      clipBehavior: Clip.antiAlias,
      child: LayoutBuilder(
        builder: (context, constraints) {
          final nodeWidth = constraints.maxWidth < 600 ? 90.0 : 108.0;
          const nodeHeight = 70.0;
          final layout = _treeLayout();
          final positions = layout.positions;
          Offset resolvedPosition(String nodeId) {
            final p = positions[nodeId] ?? const Offset(.5, .5);
            return Offset(.06 + p.dx * .88, .06 + p.dy * .88);
          }

          Offset centerFor(String nodeId) {
            final p = resolvedPosition(nodeId);
            return Offset(
              p.dx * (constraints.maxWidth - nodeWidth) + nodeWidth / 2,
              p.dy * (constraints.maxHeight - nodeHeight) + nodeHeight / 2,
            );
          }

          return Stack(
            children: [
              Positioned.fill(
                child: CustomPaint(
                  painter: _GraphPainter(
                    edges: layout.edges,
                    centerFor: centerFor,
                  ),
                ),
              ),
              for (final node in course.nodes)
                Positioned(
                  left:
                      resolvedPosition(node.id).dx *
                      (constraints.maxWidth - nodeWidth),
                  top:
                      resolvedPosition(node.id).dy *
                      (constraints.maxHeight - nodeHeight),
                  width: nodeWidth,
                  height: nodeHeight,
                  child: _NodeCard(
                    node: node,
                    selected: controller.selectedNode?.id == node.id,
                    onTap: () => controller.selectNode(node),
                  ),
                ),
              Positioned(
                left: 14,
                bottom: 12,
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 10,
                    vertical: 7,
                  ),
                  decoration: BoxDecoration(
                    color: _background.withValues(alpha: .82),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      const _LegendDot(_cyan),
                      Text(
                        ' ${localizations.legendLearning}',
                        style: const TextStyle(fontSize: 10, color: _muted),
                      ),
                      const SizedBox(width: 10),
                      const _LegendDot(_violet),
                      Text(
                        ' ${localizations.legendPracticed}',
                        style: const TextStyle(fontSize: 10, color: _muted),
                      ),
                      const SizedBox(width: 10),
                      const _LegendDot(Color(0xFF465365)),
                      Text(
                        ' ${localizations.legendLocked}',
                        style: const TextStyle(fontSize: 10, color: _muted),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          );
        },
      ),
    );
  }
}

class _GraphPainter extends CustomPainter {
  _GraphPainter({required this.edges, required this.centerFor});
  final List<LearningEdge> edges;
  final Offset Function(String) centerFor;

  @override
  void paint(Canvas canvas, Size size) {
    final grid = Paint()
      ..color = const Color(0xFF15202C)
      ..strokeWidth = .5;
    for (double x = 0; x < size.width; x += 34) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), grid);
    }
    for (double y = 0; y < size.height; y += 34) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), grid);
    }
    final edgePaint = Paint()
      ..color = _cyan.withValues(alpha: .28)
      ..strokeWidth = 1.4
      ..style = PaintingStyle.stroke;
    for (final edge in edges) {
      try {
        final start = centerFor(edge.sourceNodeId);
        final end = centerFor(edge.targetNodeId);
        final path = Path()
          ..moveTo(start.dx, start.dy)
          ..cubicTo(
            start.dx,
            (start.dy + end.dy) / 2,
            end.dx,
            (start.dy + end.dy) / 2,
            end.dx,
            end.dy,
          );
        canvas.drawPath(path, edgePaint);
      } catch (_) {
        continue;
      }
    }
  }

  @override
  bool shouldRepaint(covariant _GraphPainter oldDelegate) => true;
}

class _NodeCard extends StatelessWidget {
  const _NodeCard({
    required this.node,
    required this.selected,
    required this.onTap,
  });
  final LearningNode node;
  final bool selected;
  final VoidCallback onTap;

  Color get color {
    if (node.progress >= 100) return _cyan;
    if (node.masteryState == 'locked') return const Color(0xFF596678);
    if (node.masteryState == 'practiced') return _violet;
    if (node.masteryState == 'recommended') return _amber;
    return _cyan;
  }

  @override
  Widget build(BuildContext context) => Material(
    color: Colors.transparent,
    child: InkWell(
      key: Key('node-${node.slug}'),
      onTap: onTap,
      borderRadius: BorderRadius.circular(16),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 180),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 7),
        decoration: BoxDecoration(
          color: selected
              ? color.withValues(alpha: .17)
              : _surfaceHigh.withValues(alpha: .94),
          borderRadius: BorderRadius.circular(16),
          border: Border.all(
            color: selected ? color : color.withValues(alpha: .38),
            width: selected ? 1.8 : 1,
          ),
          boxShadow: selected
              ? [BoxShadow(color: color.withValues(alpha: .2), blurRadius: 20)]
              : null,
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Text(
              '${node.progress}',
              style: TextStyle(
                fontSize: 10,
                color: color,
                fontWeight: FontWeight.w800,
              ),
            ),
            const SizedBox(height: 3),
            Text(
              node.title,
              maxLines: 2,
              textAlign: TextAlign.center,
              overflow: TextOverflow.ellipsis,
              style: const TextStyle(
                fontSize: 10.5,
                fontWeight: FontWeight.w700,
                height: 1.12,
              ),
            ),
          ],
        ),
      ),
    ),
  );
}

class _LearningPanel extends StatelessWidget {
  const _LearningPanel({required this.controller});
  final LearningController controller;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final node = controller.selectedNode;
    final activity = controller.activity;
    return Container(
      key: const Key('learning-panel'),
      decoration: const BoxDecoration(
        color: Color(0xF20E141D),
        border: Border(
          left: BorderSide(color: Color(0xFF202A37)),
          top: BorderSide(color: Color(0xFF202A37)),
        ),
      ),
      child: node == null
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(36),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Icon(
                      Icons.touch_app_outlined,
                      color: _muted,
                      size: 30,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      localizations.selectGraphNode,
                      style: const TextStyle(fontWeight: FontWeight.w700),
                    ),
                    const SizedBox(height: 6),
                    Text(
                      localizations.selectGraphNodeDescription,
                      textAlign: TextAlign.center,
                      style: const TextStyle(
                        color: _muted,
                        fontSize: 12,
                        height: 1.5,
                      ),
                    ),
                  ],
                ),
              ),
            )
          : SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(22, 22, 22, 28),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  _Eyebrow(localizations.currentNodeEyebrow),
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          node.title,
                          style: Theme.of(context).textTheme.titleLarge,
                        ),
                      ),
                      _ProgressRing(progress: node.progress),
                    ],
                  ),
                  const SizedBox(height: 22),
                  Container(
                    padding: const EdgeInsets.all(17),
                    decoration: BoxDecoration(
                      color: _surface,
                      borderRadius: BorderRadius.circular(17),
                      border: Border.all(color: const Color(0xFF222D3A)),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            const Icon(
                              Icons.auto_awesome,
                              color: _cyan,
                              size: 16,
                            ),
                            const SizedBox(width: 8),
                            Text(
                              localizations.nexusTutor,
                              style: const TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.w800,
                                letterSpacing: 1.2,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 13),
                        Text(activity?.content ?? localizations.tutorLoading),
                        const SizedBox(height: 13),
                        _Insight(
                          activity?.insight ??
                              localizations.waitingLearningActivity,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 18),
                  _Eyebrow(localizations.nextAction),
                  const SizedBox(height: 9),
                  Text(
                    localizations.graphPracticeDescription,
                    style: const TextStyle(
                      color: _muted,
                      fontSize: 12,
                      height: 1.5,
                    ),
                  ),
                  const SizedBox(height: 14),
                  SizedBox(
                    width: double.infinity,
                    child: FilledButton.icon(
                      key: const Key('open-practice'),
                      onPressed: controller.busy
                          ? null
                          : () => controller.selectDestination(
                              WorkspaceDestination.practice,
                            ),
                      style: FilledButton.styleFrom(
                        backgroundColor: _cyan,
                        foregroundColor: _background,
                        padding: const EdgeInsets.symmetric(vertical: 15),
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(13),
                        ),
                      ),
                      icon: const Icon(Icons.psychology_alt_outlined, size: 17),
                      label: Text(
                        localizations.openPractice,
                        style: const TextStyle(fontWeight: FontWeight.w800),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }
}

class _EvaluationCard extends StatelessWidget {
  const _EvaluationCard({required this.review});
  final RuntimeReview review;
  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: _violet.withValues(alpha: .08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: _violet.withValues(alpha: .35)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Icon(Icons.fact_check_outlined, color: _violet, size: 18),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  localizations.evaluatorResult,
                  style: const TextStyle(
                    fontSize: 11,
                    fontWeight: FontWeight.w800,
                    letterSpacing: 1,
                  ),
                ),
              ),
              Text(
                '${(review.score * 100).round()}%',
                style: const TextStyle(
                  color: _violet,
                  fontWeight: FontWeight.w900,
                ),
              ),
            ],
          ),
          const SizedBox(height: 9),
          Text(
            review.reason,
            style: const TextStyle(fontSize: 12, color: Color(0xFFBCC5D2)),
          ),
          if (review.gaps.isNotEmpty) ...[
            const SizedBox(height: 10),
            for (final gap in review.gaps)
              Padding(
                padding: const EdgeInsets.only(bottom: 4),
                child: Text(
                  '• $gap',
                  style: const TextStyle(fontSize: 11, color: _muted),
                ),
              ),
          ],
        ],
      ),
    );
  }
}

class _ProposalCard extends StatelessWidget {
  const _ProposalCard({required this.controller, required this.proposal});
  final LearningController controller;
  final Map<String, dynamic> proposal;

  @override
  Widget build(BuildContext context) {
    final localizations = AppLocalizations.of(context)!;
    final nodes = proposal['proposed_nodes'] as List<dynamic>? ?? const [];
    final risks = proposal['risks'] as List<dynamic>? ?? const [];
    final decided = controller.reviewOutcome != null;
    final approved = controller.reviewApproved == true;
    return Container(
      key: const Key('proposal-card'),
      padding: const EdgeInsets.all(17),
      decoration: BoxDecoration(
        color: _amber.withValues(alpha: .07),
        borderRadius: BorderRadius.circular(17),
        border: Border.all(color: _amber.withValues(alpha: .38)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                decided
                    ? approved
                          ? Icons.check_circle_outline
                          : Icons.shield_outlined
                    : Icons.pause_circle_outline,
                color: decided ? _cyan : _amber,
                size: 19,
              ),
              const SizedBox(width: 8),
              Text(
                decided
                    ? localizations.humanDecisionRecorded
                    : localizations.humanReviewRequired,
                style: const TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w900,
                  letterSpacing: 1.1,
                  color: _amber,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            proposal['summary'] as String? ?? localizations.graphUpdateProposal,
            style: const TextStyle(fontWeight: FontWeight.w700, height: 1.35),
          ),
          const SizedBox(height: 8),
          Text(
            proposal['rationale'] as String? ?? '',
            style: const TextStyle(fontSize: 12, color: _muted, height: 1.45),
          ),
          const SizedBox(height: 11),
          Text(
            localizations.proposalMeta(nodes.length, risks.length),
            style: const TextStyle(
              color: _amber,
              fontSize: 11,
              fontWeight: FontWeight.w700,
            ),
          ),
          const SizedBox(height: 14),
          if (decided)
            Container(
              key: const Key('review-decision-result'),
              width: double.infinity,
              padding: const EdgeInsets.all(13),
              decoration: BoxDecoration(
                color: _cyan.withValues(alpha: .07),
                borderRadius: BorderRadius.circular(13),
                border: Border.all(color: _cyan.withValues(alpha: .2)),
              ),
              child: Text(
                approved
                    ? localizations.graphUpdateApplied(
                        controller.reviewOutcome ?? '',
                      )
                    : localizations.graphPreserved(
                        controller.reviewOutcome ?? '',
                      ),
                style: const TextStyle(
                  color: _cyan,
                  fontSize: 11,
                  fontWeight: FontWeight.w700,
                ),
              ),
            )
          else
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    key: const Key('reject-proposal'),
                    onPressed: controller.busy
                        ? null
                        : () => controller.decide(false),
                    child: Text(localizations.keepGraph),
                  ),
                ),
                const SizedBox(width: 9),
                Expanded(
                  child: FilledButton(
                    key: const Key('approve-proposal'),
                    onPressed: controller.busy
                        ? null
                        : () => controller.decide(true),
                    style: FilledButton.styleFrom(
                      backgroundColor: _amber,
                      foregroundColor: _background,
                    ),
                    child: Text(
                      localizations.applyProposal,
                      style: const TextStyle(fontWeight: FontWeight.w800),
                    ),
                  ),
                ),
              ],
            ),
        ],
      ),
    );
  }
}

class _ProgressRing extends StatelessWidget {
  const _ProgressRing({required this.progress});
  final int progress;
  @override
  Widget build(BuildContext context) => SizedBox(
    width: 44,
    height: 44,
    child: Stack(
      alignment: Alignment.center,
      children: [
        CircularProgressIndicator(
          value: progress / 100,
          backgroundColor: const Color(0xFF283241),
          color: _cyan,
          strokeWidth: 3,
        ),
        Text(
          '$progress',
          style: const TextStyle(fontSize: 10, fontWeight: FontWeight.w800),
        ),
      ],
    ),
  );
}

class _Insight extends StatelessWidget {
  const _Insight(this.text);
  final String text;
  @override
  Widget build(BuildContext context) => Container(
    padding: const EdgeInsets.all(12),
    decoration: BoxDecoration(
      color: _cyan.withValues(alpha: .06),
      borderRadius: BorderRadius.circular(12),
      border: Border(left: BorderSide(color: _cyan, width: 2)),
    ),
    child: Text(
      text,
      style: const TextStyle(
        fontSize: 11.5,
        color: Color(0xFFB9C5D1),
        height: 1.45,
      ),
    ),
  );
}

class _Eyebrow extends StatelessWidget {
  const _Eyebrow(this.text);
  final String text;
  @override
  Widget build(BuildContext context) => Row(
    mainAxisSize: MainAxisSize.min,
    children: [
      Container(
        width: 6,
        height: 6,
        decoration: const BoxDecoration(
          color: _cyan,
          shape: BoxShape.circle,
          boxShadow: [BoxShadow(color: _cyan, blurRadius: 8)],
        ),
      ),
      const SizedBox(width: 8),
      Flexible(
        child: Text(
          text,
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: const TextStyle(
            fontSize: 9,
            color: _muted,
            letterSpacing: 1.45,
            fontWeight: FontWeight.w700,
          ),
        ),
      ),
    ],
  );
}

class _LegendDot extends StatelessWidget {
  const _LegendDot(this.color);
  final Color color;
  @override
  Widget build(BuildContext context) => Container(
    width: 6,
    height: 6,
    decoration: BoxDecoration(color: color, shape: BoxShape.circle),
  );
}
