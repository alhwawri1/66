import WidgetKit
import SwiftUI

struct MasareefEntry: TimelineEntry {
    let date: Date
    let spent: String
    let remaining: String
    let budget: String
    let spentRatio: Double
    let currency: String
    let uncheckedCount: Int
    let month: String
}

struct MasareefProvider: TimelineProvider {
    private let suiteName = "group.com.alhawari.masareef"

    func placeholder(in context: Context) -> MasareefEntry {
        MasareefEntry(
            date: Date(),
            spent: "120.000",
            remaining: "380.000",
            budget: "500.000",
            spentRatio: 0.24,
            currency: "OMR",
            uncheckedCount: 3,
            month: "2026-11"
        )
    }

    func getSnapshot(in context: Context, completion: @escaping (MasareefEntry) -> Void) {
        completion(loadEntry())
    }

    func getTimeline(in context: Context, completion: @escaping (Timeline<MasareefEntry>) -> Void) {
        let entry = loadEntry()
        let timeline = Timeline(entries: [entry], policy: .after(Date().addingTimeInterval(900)))
        completion(timeline)
    }

    private func loadEntry() -> MasareefEntry {
        let defaults = UserDefaults(suiteName: suiteName)
        let spent = defaults?.string(forKey: "widget_spent") ?? "0.000"
        let remaining = defaults?.string(forKey: "widget_remaining") ?? "0.000"
        let budget = defaults?.string(forKey: "widget_budget") ?? "500.000"
        let ratio = defaults?.double(forKey: "widget_spent_ratio") ?? 0.0
        let currency = defaults?.string(forKey: "widget_currency") ?? "OMR"
        let unchecked = defaults?.integer(forKey: "widget_unchecked_count") ?? 0
        let month = defaults?.string(forKey: "widget_month") ?? ""

        return MasareefEntry(
            date: Date(),
            spent: spent,
            remaining: remaining,
            budget: budget,
            spentRatio: min(max(ratio, 0.0), 1.0),
            currency: currency,
            uncheckedCount: unchecked,
            month: month
        )
    }
}

struct MasareefWidgetView: View {
    @Environment(\.widgetFamily) var family
    var entry: MasareefEntry

    private let emerald = Color(red: 0.063, green: 0.725, blue: 0.506)
    private let cyan = Color(red: 0.024, green: 0.714, blue: 0.831)
    private let bgDark = Color(red: 0.04, green: 0.055, blue: 0.09)

    var body: some View {
        switch family {
        case .systemMedium:
            mediumWidget
        default:
            smallWidget
        }
    }

    private var smallWidget: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack {
                Text("Masareef")
                    .font(.caption.bold())
                    .foregroundStyle(emerald)
                Spacer()
                Link(destination: URL(string: "masareef://checklist")!) {
                    HStack(spacing: 3) {
                        Image(systemName: "cart.fill")
                        Text("\(entry.uncheckedCount)")
                    }
                    .font(.caption2.bold().monospacedDigit())
                    .foregroundStyle(.white)
                    .padding(.horizontal, 6)
                    .padding(.vertical, 2)
                    .background(cyan.opacity(0.35))
                    .clipShape(Capsule())
                }
            }

            Text("Remaining")
                .font(.caption2)
                .foregroundStyle(.secondary)

            Text("\(entry.remaining) \(entry.currency)")
                .font(.headline.bold().monospacedDigit())
                .foregroundStyle(.primary)
                .lineLimit(1)
                .minimumScaleFactor(0.75)

            ProgressView(value: entry.spentRatio)
                .tint(entry.spentRatio > 0.85 ? .red : emerald)

            HStack {
                Text("Spent: \(entry.spent)")
                    .font(.caption2.monospacedDigit())
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
                Spacer()
                Link(destination: URL(string: "masareef://quick-add")!) {
                    Image(systemName: "plus.circle.fill")
                        .font(.body)
                        .foregroundStyle(emerald)
                }
            }
        }
        .padding(12)
        .containerBackground(bgDark, for: .widget)
    }

    private var mediumWidget: some View {
        HStack(spacing: 12) {
            VStack(alignment: .leading, spacing: 6) {
                HStack(spacing: 6) {
                    Text("Masareef")
                        .font(.subheadline.bold())
                        .foregroundStyle(emerald)
                    if !entry.month.isEmpty {
                        Text(entry.month)
                            .font(.caption2.monospacedDigit())
                            .foregroundStyle(.secondary)
                    }
                }

                Text("Remaining Budget")
                    .font(.caption2)
                    .foregroundStyle(.secondary)

                Text("\(entry.remaining) \(entry.currency)")
                    .font(.title3.bold().monospacedDigit())
                    .lineLimit(1)
                    .minimumScaleFactor(0.75)

                ProgressView(value: entry.spentRatio)
                    .tint(entry.spentRatio > 0.85 ? .red : emerald)

                Text("Spent \(entry.spent) of \(entry.budget) \(entry.currency)")
                    .font(.caption2.monospacedDigit())
                    .foregroundStyle(.secondary)
                    .lineLimit(1)
            }

            Divider()

            VStack(alignment: .leading, spacing: 8) {
                Link(destination: URL(string: "masareef://checklist")!) {
                    VStack(alignment: .leading, spacing: 2) {
                        HStack {
                            Image(systemName: "checklist")
                                .foregroundStyle(cyan)
                            Text("Shopping")
                                .font(.caption.bold())
                        }
                        Text("\(entry.uncheckedCount) to buy")
                            .font(.caption2.monospacedDigit())
                            .foregroundStyle(.secondary)
                    }
                    .frame(maxWidth: .infinity, alignment: .leading)
                    .padding(8)
                    .background(Color.white.opacity(0.05))
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                }

                Link(destination: URL(string: "masareef://quick-add")!) {
                    HStack {
                        Image(systemName: "plus.circle.fill")
                        Text("Add Expense")
                            .font(.caption.bold())
                    }
                    .foregroundStyle(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, 8)
                    .background(LinearGradient(colors: [emerald, cyan], startPoint: .leading, endPoint: .trailing))
                    .clipShape(RoundedRectangle(cornerRadius: 10))
                }
            }
            .frame(width: 122)
        }
        .padding(12)
        .containerBackground(bgDark, for: .widget)
    }
}

@main
struct MasareefWidget: Widget {
    let kind: String = "MasareefWidget"

    var body: some WidgetConfiguration {
        StaticConfiguration(kind: kind, provider: MasareefProvider()) { entry in
            MasareefWidgetView(entry: entry)
        }
        .configurationDisplayName("Masareef Summary")
        .description("Shows remaining budget, monthly spending progress, and shopping items.")
        .supportedFamilies([.systemSmall, .systemMedium])
    }
}
