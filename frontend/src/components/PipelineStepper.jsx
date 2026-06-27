const STEPS = ['Dataset', 'Planner', 'EDA', 'Viz', 'Insights', 'Review', 'Reflect', 'Report']
const ICONS = ['D', 'P', 'E', 'V', 'I', 'R', 'F', 'T']

export default function PipelineStepper({ currentStep = -1, error = false }) {
  return (
    <div className="pipeline">
      {STEPS.map((label, i) => {
        const isDone   = i < currentStep
        const isActive = i === currentStep
        const isError  = error && i === currentStep

        let dotClass = 'step-dot'
        if (isDone)    dotClass += ' done'
        else if (isError) dotClass += ' error'
        else if (isActive) dotClass += ' active'

        return (
          <div key={label} style={{ display: 'flex', alignItems: 'center' }}>
            {i > 0 && (
              <div className={`step-connector ${i <= currentStep ? 'done' : ''}`} />
            )}
            <div className="step">
              <div className={dotClass}>
                {isDone ? '✓' : isError ? '✗' : ICONS[i]}
              </div>
              <div className="step-label">{label}</div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
