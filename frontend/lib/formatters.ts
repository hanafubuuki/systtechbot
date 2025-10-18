/**
 * Утилиты для форматирования данных
 */

/**
 * Форматирует дату в европейский формат DD.MM.YY
 * @param date - Дата в формате ISO (YYYY-MM-DD) или Date объект
 * @returns Отформатированная строка даты
 * @example formatDate('2025-10-17') // '17.10.25'
 */
export function formatDate(date: string | Date): string {
  const d = typeof date === 'string' ? new Date(date) : date
  const day = String(d.getDate()).padStart(2, '0')
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const year = String(d.getFullYear()).slice(-2)
  return `${day}.${month}.${year}`
}

/**
 * Форматирует число как процент со знаком
 * @param value - Числовое значение процента
 * @returns Отформатированная строка процента
 * @example formatPercent(12.456) // '+12.5%'
 * @example formatPercent(-8.321) // '-8.3%'
 * @example formatPercent(0) // '0.0%'
 */
export function formatPercent(value: number): string {
  const rounded = value.toFixed(1)
  const sign = value > 0 ? '+' : ''
  return `${sign}${rounded}%`
}

/**
 * Форматирует число с разделителями тысяч (пробелами)
 * @param value - Числовое значение
 * @returns Отформатированная строка числа
 * @example formatNumber(1234567) // '1 234 567'
 * @example formatNumber(42) // '42'
 */
export function formatNumber(value: number): string {
  return value.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ' ')
}

/**
 * Форматирует дробное число с заданным количеством знаков после запятой
 * @param value - Числовое значение
 * @param digits - Количество знаков после запятой (по умолчанию 1)
 * @returns Отформатированная строка числа
 * @example formatDecimal(125.456, 1) // '125.5'
 * @example formatDecimal(125.456, 2) // '125.46'
 */
export function formatDecimal(value: number, digits: number = 1): string {
  return value.toFixed(digits)
}

