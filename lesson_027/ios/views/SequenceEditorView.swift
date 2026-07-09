import SwiftUI

/// SequenceEditorView
///
/// Dumb temporal bucket editor for Claimlandia Voice.
///
/// Authority: false.
/// No fake green.
/// Before / During / After are structural buckets only.
/// No causation.
/// No diagnosis.
/// No benefits prediction.
/// No VA outcome prediction.
/// No telemetry.
/// No services.
struct SequenceEditorView: View {
    @Binding var beforeText: String
    @Binding var duringText: String
    @Binding var afterText: String

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text("Sequence")
                .font(.title2)
                .bold()

            Text("Organize what happened into before, during, and after. These are structure buckets only.")
                .font(.subheadline)

            Group {
                Text("Before")
                    .font(.headline)
                TextEditor(text: $beforeText)
                    .frame(minHeight: 120)
                    .accessibilityLabel("Before sequence editor")

                Text("During")
                    .font(.headline)
                TextEditor(text: $duringText)
                    .frame(minHeight: 120)
                    .accessibilityLabel("During sequence editor")

                Text("After")
                    .font(.headline)
                TextEditor(text: $afterText)
                    .frame(minHeight: 120)
                    .accessibilityLabel("After sequence editor")
            }

            Text("This view organizes timing only. It does not decide cause, diagnosis, rating, eligibility, service connection, or outcome.")
                .font(.footnote)
        }
        .padding()
    }
}
