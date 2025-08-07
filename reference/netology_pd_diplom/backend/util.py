def str_to_bool(value: str) -> int:
    """Преобразует строковое значение в булево (1/0).
    
    Поддерживаемые значения для True:
    'y', 'yes', 't', 'true', 'on', '1'
    
    Поддерживаемые значения для False:
    'n', 'no', 'f', 'false', 'off', '0'
    
    Args:
        value: Строка для преобразования
        
    Returns:
        1 для True, 0 для False
        
    Raises:
        ValueError: Если переданное значение не распознано
    """
    true_values = {'y', 'yes', 't', 'true', 'on', '1'}
    false_values = {'n', 'no', 'f', 'false', 'off', '0'}
    
    normalized = value.lower().strip()
    
    if normalized in true_values:
        return 1
    if normalized in false_values:
        return 0
        
    raise ValueError(f"Недопустимое значение для преобразования: '{value}'")
