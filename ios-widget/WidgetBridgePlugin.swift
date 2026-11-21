import Foundation
import Capacitor
import WidgetKit

@objc(WidgetBridgePlugin)
public class WidgetBridgePlugin: CAPPlugin, CAPBridgedPlugin {
    public let identifier = "WidgetBridgePlugin"
    public let jsName = "WidgetBridge"
    public let pluginMethods: [CAPPluginMethod] = [
        CAPPluginMethod(name: "updateWidget", returnType: CAPPluginReturnPromise)
    ]

    private let appGroupId = "group.com.alhawari.masareef"

    @objc func updateWidget(_ call: CAPPluginCall) {
        let spent = call.getString("spent") ?? "0.000"
        let remaining = call.getString("remaining") ?? "0.000"
        let budget = call.getString("budget") ?? "500.000"
        let spentRatio = call.getDouble("spentRatio") ?? 0.0
        let currency = call.getString("currency") ?? "OMR"
        let uncheckedCount = call.getInt("uncheckedCount") ?? 0
        let month = call.getString("month") ?? ""

        if let defaults = UserDefaults(suiteName: appGroupId) {
            defaults.set(spent, forKey: "widget_spent")
            defaults.set(remaining, forKey: "widget_remaining")
            defaults.set(budget, forKey: "widget_budget")
            defaults.set(spentRatio, forKey: "widget_spent_ratio")
            defaults.set(currency, forKey: "widget_currency")
            defaults.set(uncheckedCount, forKey: "widget_unchecked_count")
            defaults.set(month, forKey: "widget_month")
        }

        if #available(iOS 14.0, *) {
            WidgetCenter.shared.reloadTimelines(ofKind: "MasareefWidget")
        }

        call.resolve()
    }
}
