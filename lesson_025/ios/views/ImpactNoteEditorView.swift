import SwiftUI

/// ImpactNoteEditorView
///
/// Dumb binding-only editor surface for Claimlandia Voice.
///
/// Authority: false.
/// No fake green.
/// No transforms.
/// No services.
/// No telemetry.
/// No diagnosis.
/// No benefits prediction.
/// No VA outcome prediction.
struct ImpactNoteEditorView: View {
    @Binding var impactText: String

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            Text("Impact Note")
                .font(.title2)
                .bold()

            Text("Write what changed in daily life. Keep it observable.")
                .font(.subheadline)

            TextEditor(text: $impactText)
                .frame(minHeight: 180)
                .accessibilityLabel("Impact note editor")

            Text("This editor only mirrors what you type. It does not diagnose, predict, rate, submit, or decide.")
                .font(.footnote)
        }
        .padding()
    }
}
