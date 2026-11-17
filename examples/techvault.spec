@req(R-01, R-02)
entity Equipment {
    id: UUID,
    status: Enum(Available, Reserved, Issued, Maintenance),
    daily_rate: Decimal,
    hours_used: Integer
}

@req(R-03, R-11)
statemachine Equipment.status {
    Available -> Reserved on reserve
    Reserved -> Issued on issue
    Issued -> Available on return
    * -> Maintenance on break
}

@req(R-18, R-19)
rule CalculateFine for IssueRecord {
    let overdue_days = max(0, days_between(self.due_date, now()))
    if overdue_days > 0 then
        self.fine = overdue_days * self.equipment.daily_rate * 1.5
    else
        self.fine = 0
    end
    invariant: self.fine >= 0
}
